// npm install exifr -g


// 获取全局包的路径
// 图片源信息.js
// 图片源信息.js
import { createRequire } from 'module';

// 方法1：直接指定全局路径 npm root -g
const globalNodeModules = 'C:\\nvm4w\\nodejs\\node_modules\\';
const require = createRequire(globalNodeModules + 'exifr\\package.json');

try {
    const exifr = require(globalNodeModules + 'exifr');
    const data = await exifr.parse('C:\\Users\\a1829\\Documents\\download\\DSC04914.jpg');
    console.log(data);
} catch (error) {
    console.error('错误:', error.message);
}