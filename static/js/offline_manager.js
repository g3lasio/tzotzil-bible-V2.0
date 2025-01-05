
class OfflineManager {
    constructor() {
        this.dbName = 'bible_offline';
        this.isOnline = navigator.onLine;
        this.setupListeners();
    }

    setupListeners() {
        window.addEventListener('online', () => this.handleConnectionChange(true));
        window.addEventListener('offline', () => this.handleConnectionChange(false));
    }

    handleConnectionChange(isOnline) {
        this.isOnline = isOnline;
        this.updateUI();
    }

    updateUI() {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = this.isOnline ? 'Online' : 'Offline';
            statusElement.className = this.isOnline ? 'status-online' : 'status-offline';
        }
    }

    async verifyDatabase() {
        try {
            const db = await this.openDatabase();
            const verses = await db.get('verses', 1);
            return !!verses;
        } catch (e) {
            console.error('Error verificando base de datos:', e);
            return false;
        }
    }

    async downloadDatabase() {
        try {
            const response = await fetch('/download_bible');
            if (!response.ok) throw new Error('Error descargando base de datos');
            
            const blob = await response.blob();
            const db = await this.openDatabase();
            await db.put('database', blob);
            
            return true;
        } catch (e) {
            console.error('Error en descarga:', e);
            return false;
        }
    }
}

// Inicializar manejador
const offlineManager = new OfflineManager();
