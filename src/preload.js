import { contextBridge, ipcRenderer } from 'electron'
contextBridge.exposeInMainWorld(
  'ipc',
  {
    createDatabase: () => ipcRenderer.invoke('create-database')
  }
)