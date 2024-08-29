import { defineConfig } from 'vitepress'
import VitePressPluginAutoNavSidebar from 'vitepress-plugin-auto-nav-sidebar'
// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "applestven",
  description: "applestven blog",
  plugins: [
    VitePressPluginAutoNavSidebar({
      documentRootPath: '/', // 这是目录所在的路径 .vitepress，如果项目根目录下文档所在的文件夹是 /docs ，那么该选项的值应该设置为 docs 或 /docs
      ignoreIndexItems: true, // 首页的 index.md 文件不会被添加到侧边栏和导航栏中
      excludeFiles: [/.*demo.*/], // 忽略的文件列表，支持正则匹配
      excludeFolders: ['demo'], // 忽略的文件夹列表，支持正则匹配
      removeTitlePrefix: /^\d+-/, //
      useTitleFromFileHeading: true, // 如果设置为 true，则使用 .md 内容中的 h1 作为侧边栏和导航栏的标题 如果 h1 不存在，则使用文件名
      useTitleFromFrontmatter: true, // 如果设置为 true，则使用 .md 文件的 frontmatter 中的 title 字段作为侧边栏和导航栏的标题。如果不存在或者无法解析，则使用文件名
      useSortFromTitle: true, // 如果设置为 true，当菜单标题为数字开头时，按照数字排序。例如，如果文件为 [1-a.md , 10-a.md ,2-a.md]，最终会按照 [ 1-a.md , 2-a.md ,10-a.md] 排序
      sortMenusBy: 'frontmatterOrder', // 删除标题中的前缀，如果标题中包含该前缀，则删除 
      sortMenusOrder: 'asc', // 排序顺序，支持升序和降序。默认为升序
      collapsed: true, // // 是否默认折叠侧边栏
      debugLog: true, // 是否打印日志。如果设置为 true，则会在控制台打印生成的 sidebar 和 nav
    }),
  ],
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Examples', link: '/markdown-examples' },
    ],

    sidebar: [
      {
        text: 'Examples',
        items: [
          { text: 'Markdown Examples', link: '/markdown-examples' },
          { text: 'Runtime API Examples', link: '/api-examples' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  }
})
