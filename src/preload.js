import { contextBridge, ipcRenderer, shell } from 'electron'
contextBridge.exposeInMainWorld(
  'electron',
  {
    createDatabase: () => ipcRenderer.invoke('create-database'),
    openExternal: (url) => shell.openExternal(url)
  }
)