import { defineConfig } from 'vitepress'
import VitePressSidebar from 'vitepress-sidebar';
//https://vitepress-sidebar.jooy2.com/guide/getting-started 配置文档
const vitepressSidebarOptions = {
  /* Options... */
  debugPrint: false,
  documentRootPath: '/',
  collapsed: true,
  // rootGroupCollapsed: true,
};
export default defineConfig({
  title: "applestven",
  description: "applestven blog",
  base: '/',
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: '笔记', link: '/markdown-examples' },
    ],

    // sidebar: [
    //   {
    //     text: 'Examples',
    //     items: [
    //       { text: 'Markdown Examples', link: '/markdown-examples' },
    //       { text: 'Runtime API Examples', link: '/api-examples' }
    //     ]
    //   }
    // ],
    sidebar: VitePressSidebar.generateSidebar(vitepressSidebarOptions),

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  }
})
