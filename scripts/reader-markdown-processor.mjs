import {satteri} from '@astrojs/markdown-satteri';
import {readerMarkdown} from '../src/lib/reader-markdown.ts';

export function readerMarkdownProcessor() {
  const processor = satteri();
  return {
    name: 'reader-markdown',
    options: processor.options,
    async createRenderer(shared) {
      const renderer = await processor.createRenderer(shared);
      return {render: (content, options) => renderer.render(readerMarkdown(content), options)};
    },
  };
}
