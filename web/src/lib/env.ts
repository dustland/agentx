/**
 * Environment configuration with validation
 * Ensures critical environment variables are present
 */

class EnvironmentError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'EnvironmentError';
  }
}

function getEnvVar(key: string, defaultValue?: string): string {
  const value = process.env[key];
  
  if (!value) {
    if (defaultValue !== undefined) {
      return defaultValue;
    }
    throw new EnvironmentError(
      `Missing required environment variable: ${key}`
    );
  }
  
  return value;
}

export const env = {
  // Required in production
  JWT_SECRET: process.env.NODE_ENV === 'production' 
    ? getEnvVar('JWT_SECRET') 
    : getEnvVar('JWT_SECRET', 'dev-secret-only-for-local-development'),
  
  // API configuration
  NEXT_PUBLIC_API_URL: getEnvVar('NEXT_PUBLIC_API_URL', 'http://localhost:7770'),
  
  // Optional
  NODE_ENV: getEnvVar('NODE_ENV', 'development'),
  
  // Feature flags
  ENABLE_DEMO_USERS: getEnvVar('ENABLE_DEMO_USERS', 'true') === 'true',
} as const;

// Validate environment on module load
if (process.env.NODE_ENV === 'production') {
  if (env.JWT_SECRET === 'dev-secret-only-for-local-development') {
    throw new EnvironmentError(
      'JWT_SECRET must be set in production environment'
    );
  }
}