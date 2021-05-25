import { contextBridge, ipcRenderer, shell } from 'electron'
contextBridge.exposeInMainWorld(
  'electron',
  {
    createDatabase: () => ipcRenderer.invoke('create-database'),
    openExternal: () => shell.openExternal('https://github.com/Linnas/RNAi-designer')
  }
)