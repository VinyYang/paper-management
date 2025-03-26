import React, { useState } from 'react';
import { Modal, Form, Input, Button, Upload, Select } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { UploadFile } from 'antd/es/upload/interface';

interface Project {
  id: number;
  name: string;
  description?: string;
}

interface AddPaperModalProps {
  visible: boolean;
  loading: boolean;
  projects: Project[];
  selectedProjectId: number | null;
  onProjectChange: (projectId: number | null) => void;
  onCancel: () => void;
  onAdd: (values: any, pdfFile: any) => void;
  getTranslation: (zhText: string, enText: string) => string;
}

const AddPaperModal: React.FC<AddPaperModalProps> = ({
  visible,
  loading,
  projects,
  selectedProjectId,
  onProjectChange,
  onCancel,
  onAdd,
  getTranslation
}) => {
  const [form] = Form.useForm();
  const [pdfFile, setPdfFile] = useState<UploadFile | null>(null);
  const { Option } = Select;

  const handleCancel = () => {
    form.resetFields();
    setPdfFile(null);
    onCancel();
  };

  const handleSubmit = (values: any) => {
    onAdd(values, pdfFile);
    // 表单在成功后由父组件清空
  };

  return (
    <Modal
      title={getTranslation('添加新文献', 'Add New Paper')}
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          name="title"
          label={getTranslation('论文标题', 'Paper Title')}
          rules={[{ required: true, message: getTranslation('请输入论文标题', 'Please enter paper title') }]}
        >
          <Input placeholder={getTranslation('论文完整标题', 'Complete paper title')} />
        </Form.Item>
        
        <Form.Item
          name="authors"
          label={getTranslation('作者', 'Authors')}
          rules={[{ required: true, message: getTranslation('请输入作者信息', 'Please enter author information') }]}
        >
          <Input placeholder={getTranslation('作者名称，多个作者用逗号分隔', 'Author names, separated by commas')} />
        </Form.Item>
        
        <Form.Item
          name="journal"
          label={getTranslation('期刊/会议名称', 'Journal/Conference Name')}
        >
          <Input placeholder={getTranslation('发表的期刊或会议名称', 'Name of the journal or conference where published')} />
        </Form.Item>
        
        <Form.Item
          name="year"
          label={getTranslation('发表年份', 'Publication Year')}
        >
          <Input type="number" placeholder={getTranslation('发表年份，如2023', 'Publication year, e.g., 2023')} />
        </Form.Item>
        
        <Form.Item
          name="doi"
          label="DOI"
          rules={[
            { 
              pattern: /^[a-zA-Z0-9./\-_()（）:]+$/,
              message: getTranslation('DOI格式不正确', 'DOI format is incorrect')
            }
          ]}
        >
          <Input placeholder={getTranslation('论文的DOI标识符', 'Paper DOI identifier')} />
        </Form.Item>
        
        <Form.Item
          name="abstract"
          label={getTranslation('摘要', 'Abstract')}
        >
          <Input.TextArea rows={4} placeholder={getTranslation('论文摘要', 'Paper abstract')} />
        </Form.Item>
        
        <Form.Item
          name="keywords"
          label={getTranslation('关键词', 'Keywords')}
        >
          <Input placeholder={getTranslation('关键词，用逗号分隔', 'Keywords, separated by commas')} />
        </Form.Item>
        
        <Form.Item
          name="pdf"
          label={getTranslation('PDF文件', 'PDF File')}
          extra={getTranslation('上传PDF文件（可选）', 'Upload PDF file (optional)')}
        >
          <Upload
            beforeUpload={(file) => {
              setPdfFile(file);
              return false;
            }}
            fileList={pdfFile ? [pdfFile] : []}
            onRemove={() => setPdfFile(null)}
            accept=".pdf"
          >
            <Button icon={<UploadOutlined />}>{getTranslation('选择文件', 'Select File')}</Button>
          </Upload>
        </Form.Item>
        
        {projects.length > 0 && (
          <Form.Item
            label={getTranslation('添加到项目', 'Add to Project')}
            name="project_id"
          >
            <Select
              style={{ width: '100%' }}
              placeholder={getTranslation('选择项目', 'Select a project')}
              onChange={(value) => onProjectChange(value ? Number(value) : null)}
              value={selectedProjectId}
              allowClear
              showSearch
              optionFilterProp="children"
            >
              {projects.map(project => (
                <Option key={project.id} value={project.id}>
                  {project.name}
                  {project.description ? ` - ${project.description}` : ''}
                </Option>
              ))}
            </Select>
          </Form.Item>
        )}
        
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={handleCancel} style={{ marginRight: 8 }}>
            {getTranslation('取消', 'Cancel')}
          </Button>
          <Button type="primary" htmlType="submit" loading={loading}>
            {getTranslation('保存', 'Save')}
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

export default AddPaperModal; 