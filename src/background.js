'use strict'

import { app, protocol, BrowserWindow, session, dialog, ipcMain } from 'electron'
import { createProtocol } from 'vue-cli-plugin-electron-builder/lib'
import installExtension, { VUEJS_DEVTOOLS } from 'electron-devtools-installer'
const path = require('path')
const os = require('os')
const isDevelopment   = process.env.NODE_ENV !== 'production'
const vueDevToolsPath = path.join(os.homedir(), '/AppData/Local/Google/Chrome/User Data/Default/Extensions/nhdogjmejiglipccpnnnanhbledajbpd/5.3.4_0')
const appPath         = app.getAppPath();
// const spawn = require("await-spawn");
const { spawn, exec } = require("child_process");
var prodPath          = path.join(process.resourcesPath, 'rnai');
var devPath  = path.join(process.cwd(), 'rnai');
const isProduction = process.env.NODE_ENV === "production";
var backend = null;
// Scheme must be registered before the app is ready
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
])

async function createWindow() {

  if(isDevelopment) {
    backend = spawn(path.join(devPath, 'python', 'python.exe'), ['manage.py', 'runserver'], {cwd:devPath})
    
    backend.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
    });

    backend.stderr.on('data', (data) => {
      data = data.toString('utf-8').trim()
      console.error(`stderr: ${data}`);
    });

    backend.on('close', (code) => {
      console.log(`child process exited with code ${code}`);
    });
  } else if ( isProduction) {
    
    backend = await spawn(path.join(prodPath, 'python', 'python.exe'), ['manage.py', 'runserver'], {cwd:prodPath})
      
    
    backend.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
    });

    backend.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
    });

    backend.on('close', (code) => {
      console.log(`child process exited with code ${code}`);
    });
  }

  const win = new BrowserWindow({
    show:false,
    minHeight:600,
    minWidth:900,
    icon: "./DNA.ico",
    webPreferences: {
      
      // Use pluginOptions.nodeIntegration, leave this alone
      // See nklayman.github.io/vue-cli-plugin-electron-builder/guide/security.html#node-integration for more info
      nodeIntegration: process.env.ELECTRON_NODE_INTEGRATION,
      contextIsolation: !process.env.ELECTRON_NODE_INTEGRATION,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Load the url of the dev server if in development mode
    await win.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    if (!process.env.IS_TEST) win.webContents.openDevTools()
  } else {
    createProtocol('app')
    // Load the index.html when not in development
    win.loadURL('app://./index.html')
  }
  win.maximize();
  win.show();
  
}

ipcMain.handle('create-database', (event) => 
  dialog.showOpenDialog({
    title: "New Database",
    filters: {
      name:"Sequence",
      extensions:['fasta', 'fas', 'txt']
    },
    properties:['openFile']
  })
)

ipcMain.handle('exportAsExcel', (event) => 
  dialog.showSaveDialog({
    title: "Export as excel",
    filters: {
      name:"xslx",
      extensions:['xlsx']
    }
  })
)

ipcMain.handle('getAppPath', e => path.dirname(appPath)

)
      
ipcMain.handle('share_database', e => 
  dialog.showOpenDialog({
    title: "Save archive to...",
    properties:['openDirectory']
  })
)

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    exec(
       `taskkill /PID ${backend.pid} /T /F`,
        (error, stdout, stderr) => {
         if (error) {
           console.error(`exec error: ${error}`);
           return;
         }
         console.log(`stdout: ${stdout}`);
         console.error(`stderr: ${stderr}`);
         app.quit();
        }
       )
  }
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', () => {
  // await session.defaultSession.loadExtension(vueDevToolsPath)
  createWindow()
})

// Exit cleanly on request from parent process in development mode.
if (isDevelopment) {
  if (process.platform === 'win32') {
    process.on('message', (data) => {
      if (data === 'graceful-exit') {
        backend.kill();
        app.quit()
      }
    })
  } else {
    process.on('SIGTERM', () => {
      app.quit()
    })
  }
}
