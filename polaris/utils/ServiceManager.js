const { spawn } = require('child_process');
const path = require('path');
const Logger = require('./logger');
const fetch = require('node-fetch');
const fs = require('fs');
const os = require('os');
const { app } = require('electron');

class ServiceManager {
    constructor() {
        // Singleton pattern
        if (ServiceManager.instance) {
            return ServiceManager.instance;
        }
        ServiceManager.instance = this;

        // Determine executable paths based on platform
        const platform = os.platform();
        const isDevMode = !app.isPackaged;

        // Base directory for executables
        let executablesDir;
        if (isDevMode) {
            // In development, look for executables in a relative path
            executablesDir = path.join(process.cwd(), 'dist');
        } else {
            // In production, look in the resources directory
            executablesDir = path.join(process.resourcesPath, 'bin');
        }

        // Define services with their executables and health endpoints
        this.services = {
            orakle: {
                process: null,
                url: 'http://localhost:5000/health',
                healthy: false,
                name: 'Orakle',
                executable: platform === 'win32' ? 'orakle.exe' : 'orakle',
                executablePath: path.join(executablesDir, 'orakle', platform === 'win32' ? 'orakle.exe' : 'orakle'),
                args: []
            },
            pybridge: {
                process: null,
                url: 'http://localhost:5001/health',
                healthy: false,
                name: 'Pybridge',
                executable: platform === 'win32' ? 'pybridge.exe' : 'pybridge',
                executablePath: path.join(executablesDir, 'pybridge', platform === 'win32' ? 'pybridge.exe' : 'pybridge'),
                args: []
            }
        };

        this.onProgressUpdate = null;
        this.healthCheckInterval = null;
    }

    setProgressCallback(callback) {
        this.onProgressUpdate = callback;
    }

    updateProgress(status, progress) {
        if (this.onProgressUpdate) {
            this.onProgressUpdate(status, progress);
        }
    }

    async startServices() {
        this.updateProgress('Starting services...', 10);

        // Check if executables exist
        for (const [, service] of Object.entries(this.services)) { // id, service
            if (!fs.existsSync(service.executablePath)) {
                Logger.error(`Executable not found: ${service.executablePath}`);
                this.updateProgress(`Error: ${service.name} executable not found`, 100);
                return false;
            }
        }

        // Start both services in parallel
        const startPromises = [
            this.startService('orakle'),
            this.startService('pybridge')
        ];

        this.updateProgress('Waiting for services to initialize...', 30);

        try {
            await Promise.all(startPromises);
            this.updateProgress('Services started successfully', 50);

            // Start health check monitoring
            this.startHealthCheck();

            return true;
        } catch (error) {
            Logger.error('Failed to start services:', error);
            this.updateProgress(`Error: ${error.message}`, 100);
            return false;
        }
    }

    async startService(serviceId) {
        const service = this.services[serviceId];

        return new Promise((resolve, reject) => {
            Logger.log(`Starting ${service.name} service from: ${service.executablePath}`);

            try {
                service.process = spawn(service.executablePath, service.args, {
                    stdio: 'pipe',
                    shell: false
                });

                // Handle process output
                service.process.stdout.on('data', (data) => {
                    Logger.log(`[${service.name}] ${data.toString().trim()}`);
                });

                service.process.stderr.on('data', (data) => {
                    Logger.error(`[${service.name}] ${data.toString().trim()}`);
                });

                // Handle process exit
                service.process.on('exit', (code) => {
                    if (code !== 0 && code !== null) {
                        Logger.error(`${service.name} exited with code ${code}`);
                        service.healthy = false;

                        if (this.healthCheckInterval) {
                            this.updateProgress(`${service.name} service crashed`, 100);
                        }
                    }
                });

                // Check if service starts successfully
                this.waitForHealth(serviceId, 30000)
                    .then(() => resolve())
                    .catch(err => reject(err));

            } catch (error) {
                Logger.error(`Failed to spawn ${service.name} process:`, error);
                reject(error);
            }
        });
    }

    async waitForHealth(serviceId, timeout) {
        const service = this.services[serviceId];
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            try {
                const response = await fetch(service.url);
                if (response.ok) {
                    service.healthy = true;
                    Logger.log(`${service.name} is healthy`);
                    return true;
                }
            } catch (error) {
                console.log(error);
                // Ignore errors during startup
            }

            // Wait before next attempt
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        throw new Error(`Timeout waiting for ${service.name} to become healthy`);
    }

    startHealthCheck() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }

        this.healthCheckInterval = setInterval(async () => {
            await this.checkServicesHealth();
        }, 5000);
    }

    async checkServicesHealth() {
        let allHealthy = true;
        let healthyCount = 0;
        const totalServices = Object.keys(this.services).length;

        for (const [ , service] of Object.entries(this.services)) { // id,
            try {
                const response = await fetch(service.url);
                const wasHealthy = service.healthy;
                service.healthy = response.ok;

                if (service.healthy) {
                    healthyCount++;
                }

                if (!wasHealthy && service.healthy) {
                    Logger.log(`${service.name} is now healthy`);
                }
                else if (wasHealthy && !service.healthy) {
                    Logger.error(`${service.name} is no longer healthy`);
                }

                if (!service.healthy) {
                    allHealthy = false;
                }
            } catch (error) {
                service.healthy = false;
                allHealthy = false;
                Logger.error(`Health check failed for ${service.name}:`, error.message);
            }
        }

        // Update progress based on health status
        if (allHealthy) {
            this.updateProgress('All services are ready', 100);
        } else {
            // Calculate progress: 40% for starting + up to 60% for health checks
            const healthProgress = Math.floor((healthyCount / totalServices) * 60);
            this.updateProgress('Waiting for services to be ready...', 40 + healthProgress);
        }

        return allHealthy;
    }

    async stopServices() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }

        const terminationPromises = [];

        for (const [ , service] of Object.entries(this.services)) { // id,
            if (service.process && !service.process.killed) {
                Logger.log(`Stopping ${service.name} service...`);

                // Create a promise for this service's termination
                const terminationPromise = new Promise((resolve) => {
                    // Try graceful shutdown first
                    service.process.kill('SIGTERM');

                    // Set up event listener for process exit
                    service.process.once('exit', () => {
                        Logger.log(`${service.name} service terminated successfully`);
                        service.healthy = false;
                        resolve();
                    });

                    // Force kill after timeout if still running
                    setTimeout(() => {
                        if (service.process && !service.process.killed) {
                            Logger.log(`Force killing ${service.name} service with SIGKILL`);
                            service.process.kill('SIGKILL');
                            // The 'exit' handler above will still resolve the promise
                        }
                    }, 5000);
                });

                terminationPromises.push(terminationPromise);
            }
        }

        // Wait for all services to terminate
        if (terminationPromises.length > 0) {
            Logger.log(`Waiting for ${terminationPromises.length} services to terminate...`);
            await Promise.all(terminationPromises);
            Logger.log('All services stopped successfully');
        } else {
            Logger.log('No active services to stop');
        }

        return true;
    }

    isAllHealthy() {
        return Object.values(this.services).every(service => service.healthy);
    }

}

module.exports = new ServiceManager();
