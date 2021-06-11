import { contextBridge, ipcRenderer, shell } from 'electron'
contextBridge.exposeInMainWorld(
  'electron',
  {
    createDatabase: () => ipcRenderer.invoke('create-database'),
    getAppPath: () => ipcRenderer.invoke('getAppPath'),
    shareDatabase: () => ipcRenderer.invoke('share_database'),
    openExternal: (url) => shell.openExternal(url)
  }
)