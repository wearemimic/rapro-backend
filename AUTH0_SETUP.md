# Auth0 Integration Setup for RetirementAdvisorPro

This document provides comprehensive instructions on how to set up Auth0 authentication for the RetirementAdvisorPro application, including the complete registration flow with Stripe payment integration and coupon functionality.

## Prerequisites

1. An Auth0 account (you can sign up for free at [auth0.com](https://auth0.com))
2. Access to the RetirementAdvisorPro codebase

## Auth0 Setup

### 1. Create a New Auth0 Application

1. Log in to your Auth0 dashboard
2. Go to "Applications" > "Applications" in the sidebar
3. Click "Create Application"
4. Name your application (e.g., "RetirementAdvisorPro")
5. Select "Single Page Application" as the application type
6. Click "Create"

### 2. Configure Application Settings

In your new application settings:

1. Under "Allowed Callback URLs", add:
   ```
   http://localhost:3000/auth/callback
   ```

2. Under "Allowed Logout URLs", add:
   ```
   http://localhost:3000/login
   ```

3. Under "Allowed Web Origins", add:
   ```
   http://localhost:3000
   ```

4. Under "Allowed Origins (CORS)", add:
   ```
   http://localhost:3000
   ```

5. Save changes

### 3. Set Up Social Connections

To enable social logins:

1. Go to "Authentication" > "Social" in the sidebar
2. Enable the connections you want (Google, Facebook, Apple, etc.)
3. Configure each connection with the appropriate credentials from the respective platforms

### 4. Create API

1. Go to "Applications" > "APIs" in the sidebar
2. Click "Create API"
3. Name your API (e.g., "RetirementAdvisorPro API")
4. Set the identifier to `https://api.retirementadvisorpro.com` (or your preferred audience value)
5. Select RS256 as the signing algorithm
6. Click "Create"

### 5. Configure Environment Variables

#### Frontend (.env file)

Create a `.env` file in the `frontend` directory with the following content:

```
# Auth0 Configuration
VITE_AUTH0_DOMAIN=your-auth0-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-auth0-client-id
VITE_AUTH0_AUDIENCE=https://api.retirementadvisorpro.com
VITE_AUTH0_CALLBACK_URL=http://localhost:3000/auth/callback
VITE_AUTH0_LOGOUT_URL=http://localhost:3000/login

# API URLs
VITE_API_URL=http://localhost:8000/api
```

Replace `your-auth0-domain.auth0.com` and `your-auth0-client-id` with your actual Auth0 domain and client ID.

#### Backend (Environment Variables)

Set the following environment variables for your backend:

```
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_CLIENT_ID=your-auth0-client-id
AUTH0_CLIENT_SECRET=your-auth0-client-secret
AUTH0_ALGORITHM=RS256
```

You can find your client secret in your Auth0 application settings.

## Testing the Integration

1. Start your frontend and backend servers
2. Navigate to the login page
3. Try logging in with email/password
4. Try logging in with a social provider
5. Verify that you are redirected to the dashboard after successful authentication

## Troubleshooting

### Common Issues:

1. **Callback URL errors**: Make sure your callback URL in Auth0 settings exactly matches the URL in your application.

2. **CORS errors**: Ensure that your Auth0 application has the correct allowed origins.

3. **Token validation errors**: Check that your backend is correctly configured with the right Auth0 domain and algorithm.

4. **Social login errors**: Verify that your social connections are properly set up in Auth0 and that you've completed all required steps for each provider.

For more help, refer to the [Auth0 documentation](https://auth0.com/docs). 