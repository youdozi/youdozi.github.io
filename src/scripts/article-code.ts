import copy from '../lib/code-copy-ui.json';
import {mountCodeTools} from './code-tools';
const lang=document.documentElement.lang as keyof typeof copy;
const labels=copy[lang] ?? copy.en;
for (const prose of document.querySelectorAll('.article .prose')) {
  mountCodeTools(prose,labels,navigator.clipboard);
}
