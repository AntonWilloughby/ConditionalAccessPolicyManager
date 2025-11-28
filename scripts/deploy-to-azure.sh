#!/bin/bash
# =============================================================================
# CA Policy Manager - Automated Azure Deployment (Bash)
# =============================================================================
#
# This script automates the complete deployment of CA Policy Manager to Azure:
# - Creates App Service and Azure OpenAI resources
# - Configures application settings
# - Updates Azure AD redirect URI
# - Deploys application code
# - Generates and stores secrets securely
#
# Usage:
#   ./deploy-to-azure.sh -g <resource-group> -w <webapp-name> -o <openai-name>
#
# Example:
#   ./deploy-to-azure.sh -g ca-policy-rg -w my-ca-manager -o my-openai-helper
#
# Requirements: Azure CLI, Python 3.11+, Owner/Contributor access to Azure
# =============================================================================

set -e

# Default values
LOCATION="eastus2"
SKU="F1"
SKIP_APP_REG=false

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Helper functions
print_step() { echo -e "\n${CYAN}✓ $1${NC}"; }
print_success() { echo -e "  ${GREEN}✓ $1${NC}"; }
print_info() { echo -e "  ${YELLOW}ℹ $1${NC}"; }
print_error() { echo -e "  ${RED}✗ $1${NC}"; }

# Parse arguments
while getopts "g:w:o:l:s:h" opt; do
    case $opt in
        g) RESOURCE_GROUP="$OPTARG" ;;
        w) WEBAPP_NAME="$OPTARG" ;;
        o) OPENAI_NAME="$OPTARG" ;;
        l) LOCATION="$OPTARG" ;;
        s) SKU="$OPTARG" ;;
        h) 
            echo "Usage: $0 -g <resource-group> -w <webapp-name> -o <openai-name> [-l location] [-s sku]"
            echo "  -g  Resource group name (required)"
            echo "  -w  Web app name (required)"
            echo "  -o  Azure OpenAI resource name (required)"
            echo "  -l  Azure location (default: eastus2)"
            echo "  -s  App Service SKU (default: F1, options: F1, B1, B2, S1, P1v2)"
            exit 0
            ;;
        *) 
            print_error "Invalid option. Use -h for help."
            exit 1
            ;;
    esac
done

# Check required parameters
if [ -z "$RESOURCE_GROUP" ] || [ -z "$WEBAPP_NAME" ] || [ -z "$OPENAI_NAME" ]; then
    print_error "Missing required parameters. Use -h for help."
    exit 1
fi

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       CA Policy Manager - Automated Azure Deployment         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# =============================================================================
# Step 1: Verify Prerequisites
# =============================================================================
print_step "Checking prerequisites..."

# Check Azure CLI
if ! command -v az &> /dev/null; then
    print_error "Azure CLI not found. Install from: https://aka.ms/installazurecli"
    exit 1
fi
AZ_VERSION=$(az version --query '"azure-cli"' -o tsv 2>/dev/null)
print_success "Azure CLI installed (version $AZ_VERSION)"

# Check if logged in
if ! az account show &> /dev/null; then
    print_info "Not logged in to Azure. Launching browser..."
    az login
fi

ACCOUNT_NAME=$(az account show --query user.name -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
print_success "Logged in as: $ACCOUNT_NAME"
print_info "Subscription: $SUBSCRIPTION_NAME"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python not found. Install Python 3.11+ from: https://www.python.org"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
PYTHON_VERSION=$($PYTHON_CMD --version)
print_success "Python installed: $PYTHON_VERSION"

# =============================================================================
# Step 2: Create Resource Group
# =============================================================================
print_step "Creating resource group '$RESOURCE_GROUP'..."

if az group exists --name "$RESOURCE_GROUP" | grep -q "true"; then
    print_info "Resource group already exists"
else
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
    print_success "Resource group created"
fi

# =============================================================================
# Step 3: Generate Secrets
# =============================================================================
print_step "Generating secure secrets..."

SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))")
print_success "Flask SECRET_KEY generated"

# =============================================================================
# Step 4: Deploy Azure OpenAI
# =============================================================================
print_step "Deploying Azure OpenAI resource '$OPENAI_NAME'..."

if az cognitiveservices account show --name "$OPENAI_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_info "Azure OpenAI resource already exists"
else
    print_info "Creating Azure OpenAI resource (this may take 2-3 minutes)..."
    az cognitiveservices account create \
        --name "$OPENAI_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --kind OpenAI \
        --sku S0 \
        --custom-domain "$OPENAI_NAME" \
        --output none
    
    print_success "Azure OpenAI resource created"
fi

# Get OpenAI endpoint and key
OPENAI_ENDPOINT=$(az cognitiveservices account show \
    --name "$OPENAI_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.endpoint -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
    --name "$OPENAI_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query key1 -o tsv)

print_success "Retrieved OpenAI credentials"

# Deploy GPT-4o-mini model
print_info "Deploying GPT-4o-mini model..."
if az cognitiveservices account deployment show \
    --name "$OPENAI_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --deployment-name gpt-4o-mini &> /dev/null; then
    print_info "Model deployment already exists"
else
    az cognitiveservices account deployment create \
        --name "$OPENAI_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --deployment-name gpt-4o-mini \
        --model-name gpt-4o-mini \
        --model-version "2024-07-18" \
        --model-format OpenAI \
        --sku-capacity 30 \
        --sku-name "Standard" \
        --output none
    
    print_success "GPT-4o-mini model deployed"
fi

# =============================================================================
# Step 5: Create App Service
# =============================================================================
print_step "Creating App Service '$WEBAPP_NAME'..."

APP_SERVICE_PLAN="$WEBAPP_NAME-plan"

# Create App Service Plan
if az appservice plan show --name "$APP_SERVICE_PLAN" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_info "App Service Plan already exists"
else
    az appservice plan create \
        --name "$APP_SERVICE_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --is-linux \
        --sku "$SKU" \
        --output none
    
    print_success "App Service Plan created ($SKU tier)"
fi

# Create Web App
if az webapp show --name "$WEBAPP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_info "Web App already exists"
else
    az webapp create \
        --name "$WEBAPP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --runtime "PYTHON:3.12" \
        --output none
    
    print_success "Web App created"
fi

WEBAPP_URL="https://$WEBAPP_NAME.azurewebsites.net"
print_info "Web App URL: $WEBAPP_URL"

# =============================================================================
# Step 6: Configure App Service Settings
# =============================================================================
print_step "Configuring application settings..."

az webapp config appsettings set \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        "SECRET_KEY=$SECRET_KEY" \
        "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT" \
        "AZURE_OPENAI_API_KEY=$OPENAI_KEY" \
        "AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini" \
        "AZURE_OPENAI_API_VERSION=2024-02-15-preview" \
        "AI_ENABLED=true" \
        "AI_PROVIDER=azure" \
        "AI_USE_MAX_COMPLETION_TOKENS=true" \
        "MSAL_TENANT_ID=organizations" \
        "MSAL_REDIRECT_PATH=/auth/callback" \
        "DEMO_MODE=false" \
        "FLASK_ENV=production" \
        "DISABLE_SSL_VERIFY=false" \
        "SESSION_TYPE=filesystem" \
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
        "ENABLE_ORYX_BUILD=true" \
    --output none

print_success "Application settings configured"

# Set startup command
az webapp config set \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app" \
    --output none

print_success "Startup command configured"

# Enable HTTPS only
az webapp update \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --https-only true \
    --output none

print_success "HTTPS-only enabled"

# Enable Always On (if not F1 tier)
if [ "$SKU" != "F1" ]; then
    az webapp config set \
        --name "$WEBAPP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --always-on true \
        --output none
    
    print_success "Always On enabled"
fi

# =============================================================================
# Step 7: Create/Update Azure AD App Registration
# =============================================================================
print_step "Configuring Azure AD App Registration..."

REDIRECT_URI="$WEBAPP_URL/auth/callback"
APP_NAME="CA Policy Manager - $WEBAPP_NAME"

# Check if app registration exists
EXISTING_APP=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv)

if [ -n "$EXISTING_APP" ]; then
    print_info "Updating existing App Registration..."
    APP_ID="$EXISTING_APP"
    
    # Update redirect URIs
    az ad app update \
        --id "$APP_ID" \
        --web-redirect-uris "$REDIRECT_URI" \
        --output none
    
    print_success "App Registration updated (Client ID: $APP_ID)"
else
    print_info "Creating new App Registration..."
    
    # Create app registration
    APP_ID=$(az ad app create \
        --display-name "$APP_NAME" \
        --sign-in-audience AzureADMultipleOrgs \
        --web-redirect-uris "$REDIRECT_URI" \
        --enable-id-token-issuance true \
        --query appId -o tsv)
    
    print_success "App Registration created (Client ID: $APP_ID)"
    
    # Add Microsoft Graph API permissions
    print_info "Adding Microsoft Graph API permissions..."
    
    # Policy.Read.All (delegated) - 37f7f235-527c-4136-accd-4a02d197296e
    az ad app permission add \
        --id "$APP_ID" \
        --api 00000003-0000-0000-c000-000000000000 \
        --api-permissions 37f7f235-527c-4136-accd-4a02d197296e=Scope \
        --output none
    
    # Application.Read.All (delegated) - c79f8feb-a9db-4090-85f9-90d820caa0eb
    az ad app permission add \
        --id "$APP_ID" \
        --api 00000003-0000-0000-c000-000000000000 \
        --api-permissions c79f8feb-a9db-4090-85f9-90d820caa0eb=Scope \
        --output none
    
    print_success "API permissions added"
    print_info "Admin must grant consent in Azure Portal → App Registrations → $APP_NAME → API permissions"
fi

# Update Web App with MSAL_CLIENT_ID
az webapp config appsettings set \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings "MSAL_CLIENT_ID=$APP_ID" \
    --output none

print_success "MSAL_CLIENT_ID configured in Web App"

# =============================================================================
# Step 8: Deploy Application Code
# =============================================================================
print_step "Deploying application code..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_FOLDER="$SCRIPT_DIR/CA_Policy_Manager_Web"

if [ ! -d "$APP_FOLDER" ]; then
    print_error "CA_Policy_Manager_Web folder not found at: $APP_FOLDER"
    print_info "Please run this script from the repository root directory"
    exit 1
fi

# Create deployment package
DEPLOY_ZIP="$SCRIPT_DIR/deploy.zip"
print_info "Creating deployment package..."

cd "$APP_FOLDER"
rm -f "$DEPLOY_ZIP"
zip -r "$DEPLOY_ZIP" . -x "*.pyc" "*__pycache__*" ".env" ".venv/*" "data/uploads/*" "data/backups/*" > /dev/null
cd - > /dev/null

print_success "Deployment package created"

# Deploy to Azure
print_info "Uploading to Azure (this may take 2-3 minutes)..."
az webapp deployment source config-zip \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --src "$DEPLOY_ZIP" \
    --output none

rm -f "$DEPLOY_ZIP"
print_success "Application code deployed"

# =============================================================================
# Step 9: Enable Logging
# =============================================================================
print_step "Enabling application logging..."

az webapp log config \
    --name "$WEBAPP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --application-logging filesystem \
    --detailed-error-messages true \
    --failed-request-tracing true \
    --web-server-logging filesystem \
    --output none

print_success "Diagnostic logging enabled"

# =============================================================================
# Step 10: Summary and Next Steps
# =============================================================================
echo -e "\n${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           🎉 DEPLOYMENT SUCCESSFUL! 🎉                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "\n${CYAN}📊 DEPLOYMENT SUMMARY${NC}"
echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${YELLOW}🌐 Web Application:${NC}"
echo -e "   URL:              $WEBAPP_URL"
echo -e "   ${GRAY}Name:             $WEBAPP_NAME${NC}"
echo -e "   ${GRAY}Resource Group:   $RESOURCE_GROUP${NC}"
echo -e "   ${GRAY}Pricing Tier:     $SKU${NC}"

echo -e "\n${YELLOW}🤖 Azure OpenAI:${NC}"
echo -e "   Endpoint:         $OPENAI_ENDPOINT"
echo -e "   ${GRAY}Resource Name:    $OPENAI_NAME${NC}"
echo -e "   ${GRAY}Model:            gpt-4o-mini${NC}"

echo -e "\n${YELLOW}🔐 Azure AD App Registration:${NC}"
echo -e "   Client ID:        $APP_ID"
echo -e "   ${GRAY}Redirect URI:     $REDIRECT_URI${NC}"

echo -e "\n${CYAN}📋 NEXT STEPS${NC}"
echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${YELLOW}1. Grant Admin Consent for API Permissions (REQUIRED):${NC}"
echo -e "   ${CYAN}The script created an App Registration called 'CA Policy Manager - $WEBAPP_NAME'${NC}"
echo -e "   ${CYAN}You need to grant admin consent for it to access Microsoft Graph API.${NC}"
echo -e ""
echo -e "   ${GRAY}Steps:${NC}"
echo -e "   ${GRAY}1. Azure Portal → Azure Active Directory → App Registrations${NC}"
echo -e "   ${GRAY}2. Click 'All applications' tab${NC}"
echo -e "   ${GRAY}3. Find and click: CA Policy Manager - $WEBAPP_NAME${NC}"
echo -e "   ${GRAY}4. Click 'API permissions' in left menu${NC}"
echo -e "   ${GRAY}5. Click 'Grant admin consent for [your tenant]' button${NC}"
echo -e "   ${GRAY}6. Click 'Yes' to confirm${NC}"

echo -e "\n${YELLOW}2. Wait for Deployment to Complete (~2-3 minutes):${NC}"
echo -e "   ${GRAY}Monitor: Azure Portal → $WEBAPP_NAME → Deployment Center → Logs${NC}"

echo -e "\n${YELLOW}3. Test Your Application:${NC}"
echo -e "   Navigate to: $WEBAPP_URL"
echo -e "   ${GRAY}Click 'Sign In' to authenticate${NC}"
echo -e "   ${GRAY}Try the AI Policy Explainer feature${NC}"

echo -e "\n${YELLOW}4. View Logs (if needed):${NC}"
echo -e "   ${GRAY}Azure Portal → $WEBAPP_NAME → Log stream${NC}"

echo -e "\n${CYAN}💡 USEFUL COMMANDS${NC}"
echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${YELLOW}# View real-time logs:${NC}"
echo -e "${GRAY}az webapp log tail --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP${NC}"

echo -e "\n${YELLOW}# Restart web app:${NC}"
echo -e "${GRAY}az webapp restart --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP${NC}"

echo -e "\n${YELLOW}# Scale up to B1 tier:${NC}"
echo -e "${GRAY}az appservice plan update --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku B1${NC}"

echo -e "\n${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Save deployment info
cat > deployment-info.json << EOF
{
  "deploymentDate": "$(date -u +"%Y-%m-%d %H:%M:%S")",
  "webAppUrl": "$WEBAPP_URL",
  "webAppName": "$WEBAPP_NAME",
  "resourceGroup": "$RESOURCE_GROUP",
  "location": "$LOCATION",
  "sku": "$SKU",
  "openAIEndpoint": "$OPENAI_ENDPOINT",
  "openAIResourceName": "$OPENAI_NAME",
  "clientId": "$APP_ID"
}
EOF

print_info "Deployment details saved to: deployment-info.json"

echo -e "${GREEN}🚀 Deployment complete! Your app will be ready in 2-3 minutes.${NC}"
echo ""
