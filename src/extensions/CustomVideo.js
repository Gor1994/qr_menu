// extensions/CustomVideo.js
import { Node } from '@tiptap/core'

export const CustomVideo = Node.create({
  name: 'customVideo',
  group: 'block',
  selectable: true,
  atom: true,

  addAttributes() {
    return {
      src: { default: null },
      type: { default: 'video/mp4' },
    }
  },

  parseHTML() {
    return [{
      tag: 'video',
    }]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'video',
      { controls: '', style: 'max-width: 100%;', ...HTMLAttributes },
      ['source', { src: HTMLAttributes.src, type: HTMLAttributes.type }]
    ]
  },
})
