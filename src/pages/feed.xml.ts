// Existing subscribers continue to receive the Korean feed.
import { GET as feed } from './[lang]/feed.xml';
export function GET({ site }: { site: URL }) { return feed({ site, params: { lang: 'ko' } }); }
