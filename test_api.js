const fetch = require('node-fetch');

// 基础配置
const API_BASE = 'http://localhost:8003/api';
let token = null;

// 辅助函数: 发送请求并处理结果
async function sendRequest(url, method = 'GET', body = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const options = {
    method,
    headers,
  };
  
  if (body && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(`${API_BASE}${url}`, options);
    const data = await response.json();
    return { success: response.ok, status: response.status, data };
  } catch (error) {
    console.error(`请求失败: ${url}`, error);
    return { success: false, error };
  }
}

// 1. 登录获取token
async function login(username, password) {
  const result = await sendRequest('/token', 'POST', {
    username,
    password
  });
  
  if (result.success && result.data.access_token) {
    token = result.data.access_token;
    console.log('登录成功，获取token');
    return true;
  }
  
  console.error('登录失败');
  return false;
}

// 2. 获取项目列表
async function getProjects() {
  const result = await sendRequest('/projects/');
  if (result.success) {
    console.log('项目列表:', JSON.stringify(result.data, null, 2));
    return result.data;
  }
  
  console.error('获取项目列表失败');
  return [];
}

// 3. 获取项目详情
async function getProject(projectId) {
  const result = await sendRequest(`/projects/${projectId}`);
  if (result.success) {
    console.log(`项目 ${projectId} 详情:`, JSON.stringify(result.data, null, 2));
    return result.data;
  }
  
  console.error(`获取项目 ${projectId} 详情失败`);
  return null;
}

// 4. 获取论文列表
async function getPapers() {
  const result = await sendRequest('/papers/');
  if (result.success) {
    console.log('论文列表:', JSON.stringify(result.data, null, 2));
    return result.data;
  }
  
  console.error('获取论文列表失败');
  return [];
}

// 5. 将论文添加到项目
async function addPaperToProject(projectId, paperId) {
  const result = await sendRequest(`/projects/${projectId}/papers/${paperId}`, 'POST');
  if (result.success) {
    console.log(`成功将论文 ${paperId} 添加到项目 ${projectId}`);
    return true;
  }
  
  console.error(`将论文 ${paperId} 添加到项目 ${projectId} 失败`);
  return false;
}

// 6. 更新论文的项目关联
async function updatePaperProject(paperId, projectId) {
  const result = await sendRequest(`/papers/${paperId}`, 'PUT', {
    project_id: projectId
  });
  
  if (result.success) {
    console.log(`成功更新论文 ${paperId} 的项目关联为 ${projectId}`);
    return true;
  }
  
  console.error(`更新论文 ${paperId} 的项目关联失败`);
  return false;
}

// 主函数：测试双向互通
async function testBidirectionalConnection() {
  // 1. 登录
  const loginSuccess = await login('admin', 'admin');
  if (!loginSuccess) return;
  
  // 2. 获取项目列表
  const projects = await getProjects();
  if (!projects.length) return;
  
  // 3. 获取论文列表
  const papers = await getPapers();
  if (!papers.length) return;
  
  // 选择第一个项目和第一篇论文进行测试
  const projectId = projects[0].id;
  const paperId = papers[0].id;
  
  // 4. 获取项目详情，查看当前关联的论文
  console.log('\n--- 测试前的项目详情 ---');
  const projectBefore = await getProject(projectId);
  
  // 5. 通过项目API添加论文
  console.log('\n--- 测试通过项目API添加论文 ---');
  await addPaperToProject(projectId, paperId);
  
  // 6. 再次获取项目详情，确认论文已添加
  console.log('\n--- 测试后的项目详情 ---');
  const projectAfter = await getProject(projectId);
  
  // 7. 使用不同的项目ID
  const anotherProjectId = projects.length > 1 ? projects[1].id : projects[0].id;
  
  // 8. 通过论文API更新项目关联
  console.log('\n--- 测试通过论文API更新项目关联 ---');
  await updatePaperProject(paperId, anotherProjectId);
  
  // 9. 获取两个项目的详情，确认论文关联已更新
  console.log('\n--- 测试最终的项目详情 ---');
  await getProject(projectId);
  await getProject(anotherProjectId);
}

// 运行测试
testBidirectionalConnection().catch(console.error); 