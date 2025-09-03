<template>
  <div class="container py-5">
    <h1>Auth0 Debug Information</h1>
    
    <div class="card mb-3">
      <div class="card-header">
        <h3>Auth0 Configuration</h3>
      </div>
      <div class="card-body">
        <pre>{{ auth0Config }}</pre>
      </div>
    </div>

    <div class="card mb-3">
      <div class="card-header">
        <h3>Auth0 State</h3>
      </div>
      <div class="card-body">
        <p>Is Loading: {{ isLoading }}</p>
        <p>Is Authenticated: {{ isAuthenticated }}</p>
        <p>User: {{ user || 'Not authenticated' }}</p>
        <p>Error: {{ error || 'None' }}</p>
      </div>
    </div>

    <div class="card mb-3">
      <div class="card-header">
        <h3>Test Auth0 Login</h3>
      </div>
      <div class="card-body">
        <button @click="testLogin" class="btn btn-primary mb-2">Test loginWithRedirect</button>
        <button @click="testLoginWithGoogle" class="btn btn-success mb-2 ms-2">Test Google loginWithRedirect</button>
        <button @click="testDirectAuth0" class="btn btn-secondary mb-2 ms-2">Test Direct Auth0 URL</button>
        <button @click="testDirectGoogleAuth0" class="btn btn-warning mb-2 ms-2">Test Direct Google Auth0 URL</button>
        <div v-if="testResult" class="alert alert-info mt-3">
          <pre>{{ testResult }}</pre>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h3>Required Auth0 Dashboard Settings</h3>
      </div>
      <div class="card-body">
        <p><strong>Please ensure these URLs are configured in your Auth0 application settings:</strong></p>
        <ul>
          <li><strong>Allowed Callback URLs:</strong><br/>
            <code>http://localhost:3000/auth/callback</code>
          </li>
          <li><strong>Allowed Web Origins:</strong><br/>
            <code>http://localhost:3000</code>
          </li>
          <li><strong>Allowed Logout URLs:</strong><br/>
            <code>http://localhost:3000</code><br/>
            <code>http://localhost:3000/login</code>
          </li>
        </ul>
        <p class="text-muted">Go to Auth0 Dashboard → Applications → Your App → Settings → Application URIs</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuth0 } from '@auth0/auth0-vue';
import { auth0Config } from '@/config/auth0';

const { loginWithRedirect, user, isAuthenticated, isLoading, error } = useAuth0();
const testResult = ref(null);

const testLogin = async () => {
  try {
    testResult.value = 'Calling loginWithRedirect (no connection specified)...';
    await loginWithRedirect({
      appState: { target: '/dashboard' }
    });
  } catch (err) {
    testResult.value = `Error: ${err.message}\n${err.stack}`;
  }
};

const testLoginWithGoogle = async () => {
  try {
    testResult.value = 'Calling loginWithRedirect with Google connection...';
    await loginWithRedirect({
      appState: { target: '/dashboard' },
      authorizationParams: {
        connection: 'google-oauth2'
      }
    });
  } catch (err) {
    testResult.value = `Error: ${err.message}\n${err.stack}`;
  }
};

const testDirectAuth0 = () => {
  const authUrl = `https://${auth0Config.domain}/authorize?` +
    `response_type=code&` +
    `client_id=${auth0Config.clientId}&` +
    `redirect_uri=${encodeURIComponent(auth0Config.redirectUri)}&` +
    `scope=openid profile email&` +
    `audience=${encodeURIComponent(auth0Config.audience)}`;
  
  testResult.value = `Redirecting to basic Auth0 URL:\n${authUrl}`;
  
  setTimeout(() => {
    window.location.href = authUrl;
  }, 2000);
};

const testDirectGoogleAuth0 = () => {
  const authUrl = `https://${auth0Config.domain}/authorize?` +
    `response_type=code&` +
    `client_id=${auth0Config.clientId}&` +
    `connection=google-oauth2&` +
    `redirect_uri=${encodeURIComponent(auth0Config.redirectUri)}&` +
    `scope=openid profile email&` +
    `audience=${encodeURIComponent(auth0Config.audience)}`;
  
  testResult.value = `Redirecting to Google Auth0 URL:\n${authUrl}`;
  
  setTimeout(() => {
    window.location.href = authUrl;
  }, 2000);
};
</script>