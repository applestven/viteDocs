## generate-md-report 打印项目代码生成md文档
将代码保存到根目录 
执行 `node generate-md-report.js`

```js
const fs = require('fs')
const path = require('path')

// 配置参数
const OUTPUT_FILE = 'CODE_REPORT.md'
const IGNORE_LIST = new Set([
  'node_modules', '.git', '.vscode', 
  'package-lock.json', 'yarn.lock',
  'dist', 'build', 'coverage',
  OUTPUT_FILE // 排除自身
])

// 支持的文件类型（带语言标识）
const CODE_LANGUAGES = new Map([
  ['.js', 'javascript'],
  ['.ts', 'typescript'],
  ['.jsx', 'jsx'],
  ['.tsx', 'tsx'],
  ['.html', 'html'],
  ['.css', 'css'],
  ['.scss', 'scss'],
  ['.json', 'json'],
  ['.md', 'markdown'],
  ['.py', 'python'],
  ['.java', 'java'],
  ['.kt', 'kotlin'],
  ['.go', 'go'],
  ['.rs', 'rust']
])

function generateMDReport(dirPath, depth = 0) {
  let mdContent = ''
  const indent = '  '.repeat(depth)
  
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true })
    
    // 先处理目录
    entries.filter(e => e.isDirectory()).forEach(entry => {
      const fullPath = path.join(dirPath, entry.name)
      if (!IGNORE_LIST.has(entry.name)) {
        mdContent += `${indent}- **${entry.name}/**\n`
        mdContent += generateMDReport(fullPath, depth + 1)
      }
    })

    // 处理文件
    entries.filter(e => e.isFile()).forEach(entry => {
      const fullPath = path.join(dirPath, entry.name)
      const ext = path.extname(fullPath)
      
      if (!IGNORE_LIST.has(entry.name) && CODE_LANGUAGES.has(ext)) {
        const lang = CODE_LANGUAGES.get(ext)
        mdContent += `${indent}- 📄 ${entry.name}\n`
        mdContent += `\n\`\`\`${lang}\n`
        mdContent += readFileContent(fullPath)
        mdContent += '\n```\n\n'
      }
    })
  } catch (error) {
    console.error(`Error processing ${dirPath}:`, error.message)
  }
  
  return mdContent
}

function readFileContent(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8')
    // 清理可能破坏Markdown格式的特殊字符
    return content.replace(/```/g, 'ˋˋˋ') 
  } catch (error) {
    return `// [Error reading file: ${error.message}]`
  }
}

// 生成带前言的文件结构
const header = `# Project Code Report\n\n**Generated at**: ${new Date().toISOString()}\n\n`
const body = generateMDReport(process.cwd())
fs.writeFileSync(OUTPUT_FILE, header + body)
console.log(`Markdown报告已生成到 ${OUTPUT_FILE}`)
```

## generate-code-report 打印项目代码生成txt文档

将代码保存到根目录 

执行 `node generate-code-report.js`

```js
const fs = require('fs')
const path = require('path')

// 配置参数
const OUTPUT_FILE = 'project_code.txt'
const IGNORE_LIST = new Set([
  'node_modules',
  '.git',
  '.vscode',
  '.DS_Store',
  '.env',
  'package-lock.json',
  'yarn.lock',
  'dist',
  'build',
  'coverage'
])

// 文件类型白名单（可根据需要扩展）
const TEXT_EXTENSIONS = new Set([
  '.js', '.ts', '.jsx', '.tsx',
  '.html', '.css', '.scss',
  '.json', '.md', '.txt',
  '.vue', '.py', '.java'
])

function generateCodeReport(dirPath, baseDir = dirPath) {
  let output = ''
  
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true })
    
    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name)
      const relativePath = path.relative(baseDir, fullPath)

      if (IGNORE_LIST.has(entry.name) || IGNORE_LIST.has(relativePath)) {
        continue
      }

      if (entry.isDirectory()) {
        output += generateCodeReport(fullPath, baseDir)
      } else {
        if (shouldProcessFile(entry.name)) {
          output += `\n${'-'.repeat(80)}\n`
          output += `FILE: ${relativePath}\n`
          output += `${'-'.repeat(80)}\n`
          output += readFileContent(fullPath)
        }
      }
    }
  } catch (error) {
    console.error(`Error processing ${dirPath}:`, error.message)
  }
  
  return output
}

function shouldProcessFile(filename) {
  const ext = path.extname(filename).toLowerCase()
  return TEXT_EXTENSIONS.has(ext) && !filename.startsWith('.')
}

function readFileContent(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8') + '\n'
  } catch (error) {
    return `[Error reading file: ${error.message}]\n`
  }
}

// 执行生成
const projectRoot = process.cwd() // 获取当前工作目录
const reportContent = generateCodeReport(projectRoot)

// 写入文件
fs.writeFileSync(OUTPUT_FILE, reportContent, 'utf8')
console.log(`代码报告已生成到 ${OUTPUT_FILE}`)

```