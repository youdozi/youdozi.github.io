import {access} from 'node:fs/promises';
import {constants} from 'node:fs';
export async function chromePath(){
  const candidates=process.env.CHROME_PATH?[process.env.CHROME_PATH]:[
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/usr/bin/google-chrome','/usr/bin/google-chrome-stable','/usr/bin/chromium','/usr/bin/chromium-browser',
  ];
  for(const path of candidates){try{await access(path,constants.X_OK);return path;}catch{}}
  throw new Error('Install Chrome/Chromium or set CHROME_PATH to its executable');
}
