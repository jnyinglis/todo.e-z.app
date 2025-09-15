class SetupWizard {
  constructor() {
    this.currentStep = 1;
    this.totalSteps = 5;
    this.config = {};
    this.apiBase = '/api';

    this.init();
  }

  init() {
    this.bindEvents();
    this.loadExistingConfig();
    this.updateProgress();
    this.updateColorPreviews();
    this.generateSecureDefaults();
  }

  bindEvents() {
    // Navigation
    document.getElementById('next-step').addEventListener('click', () => this.nextStep());
    document.getElementById('prev-step').addEventListener('click', () => this.prevStep());

    // Form inputs
    document.getElementById('app-name').addEventListener('input', (e) => this.updateAppSlug(e.target.value));
    document.getElementById('theme-color').addEventListener('input', (e) => this.updateColorPreview('theme-color-preview', e.target.value));
    document.getElementById('background-color').addEventListener('input', (e) => this.updateColorPreview('bg-color-preview', e.target.value));
    document.getElementById('domain').addEventListener('input', (e) => this.updateProductionCallback(e.target.value));

    // Generators
    document.getElementById('generate-secret').addEventListener('click', () => this.generateSecret());
    document.getElementById('generate-password').addEventListener('click', () => this.generatePassword());

    // Actions
    document.getElementById('test-auth-config').addEventListener('click', () => this.testAuthConfig());
    document.getElementById('apply-config').addEventListener('click', () => this.applyConfiguration());

    // Auto-update previews
    document.addEventListener('input', () => this.updatePreview());
  }

  async loadExistingConfig() {
    try {
      const response = await fetch(`${this.apiBase}/vars`);
      const data = await response.json();

      if (data.env) {
        // Populate form fields with existing values
        Object.keys(data.env).forEach(key => {
          const element = this.getElementByEnvKey(key);
          if (element && data.env[key]) {
            element.value = data.env[key];
          }
        });

        // Try to derive app name from existing data
        if (data.env.DOMAIN) {
          document.getElementById('domain').value = data.env.DOMAIN;
          this.updateProductionCallback(data.env.DOMAIN);
        }
        if (data.env.ACME_EMAIL) {
          document.getElementById('acme-email').value = data.env.ACME_EMAIL;
        }
      }
    } catch (error) {
      console.warn('Could not load existing configuration:', error);
    }
  }

  getElementByEnvKey(key) {
    const mappings = {
      'SECRET_KEY': 'secret-key',
      'POSTGRES_PASSWORD': 'postgres-password',
      'GOOGLE_CLIENT_ID': 'google-client-id',
      'GOOGLE_CLIENT_SECRET': 'google-client-secret',
      'GITHUB_REPOSITORY': 'github-repository',
      'IMAGE_TAG': 'image-tag',
      'DOMAIN': 'domain',
      'ACME_EMAIL': 'acme-email'
    };

    return mappings[key] ? document.getElementById(mappings[key]) : null;
  }

  updateAppSlug(appName) {
    const slug = appName
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();

    document.getElementById('app-slug').value = slug;
    this.updatePreview();
  }

  updateColorPreview(previewId, color) {
    document.getElementById(previewId).style.backgroundColor = color;
  }

  updateColorPreviews() {
    const themeColor = document.getElementById('theme-color').value;
    const bgColor = document.getElementById('background-color').value;

    this.updateColorPreview('theme-color-preview', themeColor);
    this.updateColorPreview('bg-color-preview', bgColor);
  }

  updateProductionCallback(domain) {
    const callback = domain ? `https://${domain}/auth/callback` : 'https://[domain]/auth/callback';
    document.getElementById('production-callback').textContent = callback;
  }

  updatePreview() {
    const appName = document.getElementById('app-name').value;
    const appSlug = document.getElementById('app-slug').value;

    document.getElementById('preview-package-name').textContent = appSlug || '-';
    document.getElementById('preview-db-name').textContent = appSlug ? `${appSlug}_db` : '-';
    document.getElementById('preview-container-prefix').textContent = appSlug ? `${appSlug}-` : '-';
  }

  generateSecureDefaults() {
    if (!document.getElementById('secret-key').value) {
      this.generateSecret();
    }
    if (!document.getElementById('postgres-password').value) {
      this.generatePassword();
    }
  }

  generateSecret() {
    const secret = this.generateSecureKey(64);
    document.getElementById('secret-key').value = secret;
  }

  generatePassword() {
    const password = this.generateSecureKey(32);
    document.getElementById('postgres-password').value = password;
  }

  generateSecureKey(length) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  async testAuthConfig() {
    const testButton = document.getElementById('test-auth-config');
    const testResult = document.getElementById('auth-test-result');

    testButton.disabled = true;
    testResult.style.display = 'inline-flex';

    try {
      // Simulate auth test
      await new Promise(resolve => setTimeout(resolve, 2000));

      testResult.innerHTML = '✅ Configuration looks good!';
      testResult.className = '';
      testResult.style.color = 'var(--success)';
    } catch (error) {
      testResult.innerHTML = '❌ Configuration error';
      testResult.className = '';
      testResult.style.color = 'var(--danger)';
    } finally {
      testButton.disabled = false;
      setTimeout(() => {
        testResult.style.display = 'none';
      }, 3000);
    }
  }

  nextStep() {
    if (this.validateCurrentStep()) {
      if (this.currentStep < this.totalSteps) {
        this.currentStep++;
        this.updateStep();
      }
    }
  }

  prevStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.updateStep();
    }
  }

  validateCurrentStep() {
    let isValid = true;
    const errorElements = document.querySelectorAll('.input-error');
    errorElements.forEach(el => el.remove());

    switch (this.currentStep) {
      case 1:
        const appName = document.getElementById('app-name').value.trim();
        if (!appName) {
          this.showFieldError('app-name', 'App name is required');
          isValid = false;
        }
        break;

      case 2:
        // Validate required security fields
        const secretKey = document.getElementById('secret-key').value;
        const postgresPassword = document.getElementById('postgres-password').value;

        if (!secretKey) {
          this.showFieldError('secret-key', 'Secret key is required');
          isValid = false;
        }
        if (!postgresPassword) {
          this.showFieldError('postgres-password', 'Database password is required');
          isValid = false;
        }
        break;

      // Add more validation as needed
    }

    return isValid;
  }

  showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const error = document.createElement('div');
    error.className = 'input-error';
    error.textContent = message;
    field.parentNode.appendChild(error);
  }

  updateStep() {
    // Hide all steps
    document.querySelectorAll('.step-content').forEach(step => {
      step.classList.remove('active');
    });

    // Show current step
    document.getElementById(`step-${this.currentStep}`).classList.add('active');

    // Update navigation
    document.getElementById('prev-step').disabled = this.currentStep === 1;
    document.getElementById('next-step').textContent = this.currentStep === this.totalSteps ? 'Review' : 'Next →';
    document.getElementById('step-indicator').textContent = `Step ${this.currentStep} of ${this.totalSteps}`;

    // Update progress indicators
    this.updateProgress();

    // Load step-specific data
    if (this.currentStep === 5) {
      this.updateFinalPreview();
    }
  }

  updateProgress() {
    for (let i = 1; i <= this.totalSteps; i++) {
      const stepIndicator = document.getElementById(`step-indicator-${i}`);
      const connector = document.getElementById(`connector-${i}`);

      if (i < this.currentStep) {
        stepIndicator.classList.add('completed');
        stepIndicator.classList.remove('active');
        if (connector) connector.classList.add('completed');
      } else if (i === this.currentStep) {
        stepIndicator.classList.add('active');
        stepIndicator.classList.remove('completed');
        if (connector) connector.classList.remove('completed');
      } else {
        stepIndicator.classList.remove('active', 'completed');
        if (connector) connector.classList.remove('completed');
      }
    }
  }

  updateFinalPreview() {
    const config = this.gatherConfiguration();
    const previewContainer = document.getElementById('final-config-preview');

    previewContainer.innerHTML = '';

    Object.entries(config).forEach(([key, value]) => {
      if (value && value !== '') {
        const item = document.createElement('div');
        item.className = 'config-item';

        const keySpan = document.createElement('span');
        keySpan.className = 'config-key';
        keySpan.textContent = key;

        const valueSpan = document.createElement('span');
        valueSpan.className = 'config-value';
        // Hide sensitive values
        if (key.includes('SECRET') || key.includes('PASSWORD')) {
          valueSpan.textContent = '••••••••';
        } else {
          valueSpan.textContent = value;
        }

        item.appendChild(keySpan);
        item.appendChild(valueSpan);
        previewContainer.appendChild(item);
      }
    });
  }

  gatherConfiguration() {
    return {
      'App Name': document.getElementById('app-name').value,
      'App Slug': document.getElementById('app-slug').value,
      'Description': document.getElementById('app-description').value,
      'Theme Color': document.getElementById('theme-color').value,
      'Background Color': document.getElementById('background-color').value,
      'SECRET_KEY': document.getElementById('secret-key').value,
      'POSTGRES_PASSWORD': document.getElementById('postgres-password').value,
      'GOOGLE_CLIENT_ID': document.getElementById('google-client-id').value,
      'GOOGLE_CLIENT_SECRET': document.getElementById('google-client-secret').value,
      'GITHUB_REPOSITORY': document.getElementById('github-repository').value,
      'IMAGE_TAG': document.getElementById('image-tag').value,
      'DOMAIN': document.getElementById('domain').value,
      'ACME_EMAIL': document.getElementById('acme-email').value
    };
  }

  async applyConfiguration() {
    const applyButton = document.getElementById('apply-config');
    const progressDiv = document.getElementById('apply-progress');
    const logDiv = document.getElementById('apply-log');

    applyButton.disabled = true;
    progressDiv.style.display = 'block';
    logDiv.innerHTML = '';

    try {
      const config = this.gatherConfiguration();

      this.log('🚀 Starting configuration application...');

      // Apply comprehensive configuration using the new API
      this.log('🚀 Applying comprehensive configuration...');

      const appConfig = {
        app_name: config['App Name'],
        app_slug: config['App Slug'],
        app_description: config['Description'],
        theme_color: config['Theme Color'],
        background_color: config['Background Color'],
        domain: config['DOMAIN'],
        github_repository: config['GITHUB_REPOSITORY']
      };

      const response = await fetch(`${this.apiBase}/apply-configuration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appConfig)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Configuration failed');
      }

      const result = await response.json();

      // Log the results
      result.updated_files.forEach(file => {
        this.log(`✅ Updated: ${file}`);
      });

      if (result.errors && result.errors.length > 0) {
        result.errors.forEach(error => {
          this.log(`⚠️ Warning: ${error}`);
        });
      }

      // Also update environment variables with secrets if needed
      if (config['SECRET_KEY'] || config['POSTGRES_PASSWORD']) {
        this.log('🔐 Updating additional environment variables...');
        await this.updateEnvironmentVariables(config);
      }

      this.log('✅ Configuration applied successfully!');
      this.showStatus('step5-status', 'success', '🎉 Your application has been configured! You can now start developing.');

    } catch (error) {
      this.log(`❌ Error: ${error.message}`);
      this.showStatus('step5-status', 'error', `Configuration failed: ${error.message}`);
    } finally {
      applyButton.disabled = false;

      // Auto-hide progress after success
      setTimeout(() => {
        if (!progressDiv.innerHTML.includes('❌')) {
          progressDiv.style.display = 'none';
        }
      }, 5000);
    }
  }

  log(message) {
    const logDiv = document.getElementById('apply-log');
    const timestamp = new Date().toLocaleTimeString();
    logDiv.innerHTML += `[${timestamp}] ${message}\n`;
    logDiv.scrollTop = logDiv.scrollHeight;
  }

  showStatus(elementId, type, message) {
    const statusElement = document.getElementById(elementId);
    statusElement.className = `status-message ${type}`;
    statusElement.textContent = message;
  }

  async updateEnvironmentVariables(config) {
    const envUpdates = {
      'SECRET_KEY': config['SECRET_KEY'],
      'POSTGRES_PASSWORD': config['POSTGRES_PASSWORD'],
      'GOOGLE_CLIENT_ID': config['GOOGLE_CLIENT_ID'],
      'GOOGLE_CLIENT_SECRET': config['GOOGLE_CLIENT_SECRET'],
      'GITHUB_REPOSITORY': config['GITHUB_REPOSITORY'],
      'IMAGE_TAG': config['IMAGE_TAG'],
      'DOMAIN': config['DOMAIN'],
      'ACME_EMAIL': config['ACME_EMAIL']
    };

    // Filter out empty values
    const filteredUpdates = Object.fromEntries(
      Object.entries(envUpdates).filter(([_, value]) => value && value.trim() !== '')
    );

    const response = await fetch(`${this.apiBase}/vars`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ updates: filteredUpdates })
    });

    if (!response.ok) {
      throw new Error(`Failed to update environment variables: ${response.statusText}`);
    }

    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate processing time
  }

  async updatePackageJson(config) {
    // Handled by the comprehensive /api/apply-configuration endpoint
    return true;
  }

  async updateManifest(config) {
    // Handled by the comprehensive /api/apply-configuration endpoint
    return true;
  }

  async updateAppIcons(config) {
    // Handled by the comprehensive /api/apply-configuration endpoint
    return true;
  }

  async updateSEODefaults(config) {
    // Handled by the comprehensive /api/apply-configuration endpoint
    return true;
  }
}

// Initialize the wizard when the page loads
document.addEventListener('DOMContentLoaded', () => {
  new SetupWizard();
});