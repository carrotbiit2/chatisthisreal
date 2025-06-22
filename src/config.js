// API Configuration
const config = {
  development: {
    apiUrl: 'http://localhost:5000'
  },
  production: {
    apiUrl: 'https://chatisthisreal.onrender.com'
  }
};

// More explicit environment detection
const environment = import.meta.env.PROD ? 'production' : 'development';
console.log('Environment detected:', environment);
console.log('API URL:', config[environment].apiUrl);

export const API_BASE_URL = config[environment].apiUrl; 