const fs = require('fs');
const path = require('path');

// 检查 API 地址
const apiFilePath = path.join(__dirname, 'src', 'services', 'api.ts');
const apiFileContent = fs.readFileSync(apiFilePath, 'utf8');

// 输出诊断信息
console.log('前端项目检查脚本');
console.log('-----------------');

// 检查 API 地址是否正确
if (apiFileContent.includes('/api/users/token')) {
  console.log('✅ API 路径配置正确: 使用 /api/users/token');
} else if (apiFileContent.includes('/api/token')) {
  console.log('❌ API 路径配置错误: 使用 /api/token 替代 /api/users/token');
} else {
  console.log('⚠️ 未找到登录 API 路径');
}

// 检查 CORS 配置
const baseURL = apiFileContent.match(/baseURL: ['"]([^'"]+)['"]/);
if (baseURL) {
  console.log(`✅ API 基础地址: ${baseURL[1]}`);
}

// 检查 package.json
try {
  const packageJsonPath = path.join(__dirname, 'package.json');
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  
  console.log(`✅ 项目名称: ${packageJson.name}`);
  console.log(`✅ 项目版本: ${packageJson.version}`);
  
  // 检查依赖项
  const dependencies = Object.keys(packageJson.dependencies || {});
  console.log(`✅ 项目依赖项数量: ${dependencies.length}`);
  
  // 检查关键依赖项
  const requiredDeps = ['react', 'axios', 'antd'];
  for (const dep of requiredDeps) {
    if (dependencies.includes(dep)) {
      console.log(`✅ 已安装依赖: ${dep}`);
    } else {
      console.log(`❌ 缺少依赖: ${dep}`);
    }
  }
} catch (error) {
  console.log('❌ 无法读取 package.json');
}

console.log('\n前端项目检查完成。请运行 npm start 启动项目，并确保后端服务已经运行。'); 