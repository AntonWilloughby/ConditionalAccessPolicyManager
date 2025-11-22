#!/bin/bash
# Deploy Azure OpenAI resources for CA Policy Manager

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Azure OpenAI Deployment for CA Policy Manager        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}✗ Azure CLI not found${NC}"
    echo -e "${YELLOW}Please install Azure CLI from: https://docs.microsoft.com/cli/azure/install-azure-cli${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Azure CLI found${NC}"

# Login to Azure
echo -e "\n${CYAN}📋 Step 1: Azure Login${NC}"
echo "─────────────────────────"

ACCOUNT=$(az account show 2>/dev/null || echo "")
if [ -z "$ACCOUNT" ]; then
    echo -e "${YELLOW}Not logged in. Opening browser for authentication...${NC}"
    az login
fi

ACCOUNT_NAME=$(az account show --query "name" -o tsv)
ACCOUNT_ID=$(az account show --query "id" -o tsv)
USER_NAME=$(az account show --query "user.name" -o tsv)

echo -e "${GREEN}✓ Logged in as: $USER_NAME${NC}"
echo -e "${GREEN}✓ Subscription: $ACCOUNT_NAME ($ACCOUNT_ID)${NC}"

# Confirm subscription
echo -e "\n${YELLOW}Do you want to use this subscription? (Y/n): ${NC}"
read -r response
if [[ "$response" =~ ^[Nn]$ ]]; then
    echo -e "\nAvailable subscriptions:"
    az account list --output table
    echo -e "\nEnter subscription ID: "
    read -r sub_id
    az account set --subscription "$sub_id"
    ACCOUNT_NAME=$(az account show --query "name" -o tsv)
    echo -e "${GREEN}✓ Switched to: $ACCOUNT_NAME${NC}"
fi

# Get resource group name
echo -e "\n${CYAN}📦 Step 2: Resource Group${NC}"
echo "─────────────────────────"
echo -e "${YELLOW}Enter resource group name (press Enter for 'rg-capolicy-dev'): ${NC}"
read -r rg_input
RESOURCE_GROUP=${rg_input:-"rg-capolicy-dev"}

# Check if resource group exists
RG_EXISTS=$(az group exists --name "$RESOURCE_GROUP")
if [ "$RG_EXISTS" == "true" ]; then
    echo -e "${GREEN}✓ Resource group '$RESOURCE_GROUP' already exists${NC}"
else
    # Get location
    echo -e "\n${CYAN}Recommended regions for Azure OpenAI:${NC}"
    echo "  1. eastus2       (East US 2)"
    echo "  2. swedencentral (Sweden Central)"
    echo "  3. uksouth       (UK South)"
    echo "  4. westus3       (West US 3)"
    echo -e "\n${YELLOW}Enter region (press Enter for 'eastus2'): ${NC}"
    read -r location_input
    LOCATION=${location_input:-"eastus2"}
    
    echo -e "${YELLOW}Creating resource group...${NC}"
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
    echo -e "${GREEN}✓ Created resource group '$RESOURCE_GROUP' in $LOCATION${NC}"
fi

# Get OpenAI resource name
echo -e "\n${CYAN}🤖 Step 3: Azure OpenAI Resource${NC}"
echo "─────────────────────────────────"

# Generate default name with random suffix
RANDOM_SUFFIX=$(cat /dev/urandom | tr -dc 'a-z' | fold -w 4 | head -n 1)
DEFAULT_NAME="openai-capolicy-$RANDOM_SUFFIX"

echo -e "${YELLOW}Enter Azure OpenAI resource name (press Enter for '$DEFAULT_NAME'): ${NC}"
read -r name_input
OPENAI_NAME=${name_input:-"$DEFAULT_NAME"}

# Check if OpenAI resource exists
EXISTING_RESOURCE=$(az cognitiveservices account show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OPENAI_NAME" 2>/dev/null || echo "")

if [ -n "$EXISTING_RESOURCE" ]; then
    echo -e "${GREEN}✓ Azure OpenAI resource '$OPENAI_NAME' already exists${NC}"
    ENDPOINT=$(echo "$EXISTING_RESOURCE" | jq -r '.properties.endpoint')
else
    # Get location if not set
    if [ -z "$LOCATION" ]; then
        LOCATION=$(az group show --name "$RESOURCE_GROUP" --query "location" -o tsv)
    fi
    
    echo -e "${YELLOW}Creating Azure OpenAI resource...${NC}"
    echo -e "${GRAY}  Name: $OPENAI_NAME${NC}"
    echo -e "${GRAY}  Location: $LOCATION${NC}"
    echo -e "${GRAY}  SKU: S0 (Standard)${NC}"
    echo -e "\n${YELLOW}This may take 2-3 minutes...${NC}"
    
    az cognitiveservices account create \
        --name "$OPENAI_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --kind OpenAI \
        --sku S0 \
        --location "$LOCATION" \
        --yes \
        --output none || {
            echo -e "${RED}✗ Failed to create Azure OpenAI resource${NC}"
            echo -e "${YELLOW}Common issues:${NC}"
            echo -e "${YELLOW}  - Region doesn't support Azure OpenAI (try eastus2 or swedencentral)${NC}"
            echo -e "${YELLOW}  - Quota limit reached (request increase in Azure Portal)${NC}"
            echo -e "${YELLOW}  - Name already taken (try a different name)${NC}"
            exit 1
        }
    
    ENDPOINT=$(az cognitiveservices account show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$OPENAI_NAME" \
        --query "properties.endpoint" -o tsv)
    
    echo -e "${GREEN}✓ Created Azure OpenAI resource${NC}"
fi

# Deploy GPT-4o-mini model
echo -e "\n${CYAN}🎯 Step 4: Deploy GPT-4o-mini Model${NC}"
echo "────────────────────────────────────"

DEPLOYMENT_NAME="gpt-4o-mini"

# Check if deployment exists
EXISTING_DEPLOYMENT=$(az cognitiveservices account deployment show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OPENAI_NAME" \
    --deployment-name "$DEPLOYMENT_NAME" 2>/dev/null || echo "")

if [ -n "$EXISTING_DEPLOYMENT" ]; then
    echo -e "${GREEN}✓ Model deployment '$DEPLOYMENT_NAME' already exists${NC}"
else
    echo -e "${YELLOW}Deploying gpt-4o-mini model...${NC}"
    echo -e "${GRAY}  Deployment name: $DEPLOYMENT_NAME${NC}"
    echo -e "${GRAY}  Capacity: 30K TPM (tokens per minute)${NC}"
    echo -e "\n${YELLOW}This may take 1-2 minutes...${NC}"
    
    az cognitiveservices account deployment create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$OPENAI_NAME" \
        --deployment-name "$DEPLOYMENT_NAME" \
        --model-name "gpt-4o-mini" \
        --model-version "2024-07-18" \
        --model-format OpenAI \
        --sku-capacity 30 \
        --sku-name "Standard" \
        --output none || {
            echo -e "${RED}✗ Failed to deploy model${NC}"
            exit 1
        }
    
    echo -e "${GREEN}✓ Deployed gpt-4o-mini model${NC}"
fi

# Get API keys
echo -e "\n${CYAN}🔑 Step 5: Retrieve Credentials${NC}"
echo "───────────────────────────────"

API_KEY=$(az cognitiveservices account keys list \
    --resource-group "$RESOURCE_GROUP" \
    --name "$OPENAI_NAME" \
    --query "key1" -o tsv)

# Output configuration
echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║               ✓ Deployment Successful!                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}📋 Configuration Values for .env file:${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "AI_ENABLED=true"
echo "AI_PROVIDER=azure"
echo "AZURE_OPENAI_ENDPOINT=$ENDPOINT"
echo "AZURE_OPENAI_API_KEY=$API_KEY"
echo "AZURE_OPENAI_DEPLOYMENT=$DEPLOYMENT_NAME"
echo ""
echo "═══════════════════════════════════════════════════════════"

echo -e "\n${CYAN}📝 Next Steps:${NC}"
echo "  1. Copy the values above to your .env file"
echo "  2. Restart the Flask application"
echo "  3. Test AI features by clicking 'Explain with AI' on any policy"

echo -e "\n${CYAN}💰 Cost Monitoring:${NC}"
echo "  View usage at: https://portal.azure.com"

echo -e "\n${GREEN}✨ Deployment complete!${NC}\n"
