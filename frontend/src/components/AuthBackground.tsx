import React, { ReactElement, cloneElement, Children, isValidElement, useEffect, useState } from 'react';

interface AuthBackgroundProps {
  children: React.ReactNode;
  withOverlay?: boolean;
}

const AuthBackground: React.FC<AuthBackgroundProps> = ({ children, withOverlay = true }) => {
  const [scrollbarWidth, setScrollbarWidth] = useState(0);

  // 计算滚动条宽度并设置一致的页面布局
  useEffect(() => {
    // 计算滚动条宽度
    const calculatedWidth = window.innerWidth - document.documentElement.clientWidth;
    setScrollbarWidth(calculatedWidth);

    // 设置body样式，确保始终显示滚动条
    document.body.style.overflowY = 'scroll';
    
    // 添加CSS类以防止内容跳动
    document.body.classList.add('with-scrollbar');
    
    // 创建并添加样式元素
    const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      body.with-scrollbar {
        margin-right: 0 !important;
        width: 100% !important;
        position: relative;
      }
      body.with-scrollbar::before {
        content: '';
        position: fixed;
        top: 0;
        right: 0;
        width: ${calculatedWidth}px;
        height: 100%;
        background-color: transparent;
        z-index: 9999;
        pointer-events: none;
      }
    `;
    document.head.appendChild(styleElement);

    // 清理函数
    return () => {
      document.body.style.overflowY = '';
      document.body.classList.remove('with-scrollbar');
      document.head.removeChild(styleElement);
    };
  }, []);

  // 检查子组件是否包含登录注册相关的组件
  const hasLoginOrRegisterComponent = React.Children.toArray(children).some(child => {
    if (isValidElement(child)) {
      // 判断子组件的props或className中是否包含loginOrRegister字符串
      const props = child.props;
      if (props.className && typeof props.className === 'string' && props.className.includes('loginOrRegister')) {
        return true;
      }
      // 递归检查子组件的children
      if (props.children) {
        return React.Children.toArray(props.children).some(grandChild => {
          if (isValidElement(grandChild) && grandChild.props.className && 
              typeof grandChild.props.className === 'string' && 
              grandChild.props.className.includes('loginOrRegister')) {
            return true;
          }
          return false;
        });
      }
    }
    return false;
  });

  return (
    <div style={{ 
      position: 'relative', 
      width: '100%', 
      minHeight: '100vh', 
      overflowY: 'auto',
      overflowX: 'hidden',
      paddingRight: `${scrollbarWidth}px` // 添加与滚动条等宽的内边距，防止内容偏移
    }}>
      <div 
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundImage: `url('/images/auth-background.jpg')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed',
          zIndex: -1
        }}
      />
      {withOverlay && hasLoginOrRegisterComponent && (
        <div style={{ 
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(5px)',
          zIndex: -1
        }} />
      )}
      <div style={{ 
        position: 'relative', 
        zIndex: 1, 
        minHeight: '100vh',
        width: '100%',
        boxSizing: 'border-box' // 确保padding不会增加元素总宽度
      }}>
        {children}
      </div>
    </div>
  );
};

export default AuthBackground; 