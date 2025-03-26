import React, { createContext, useState, useEffect, useContext } from 'react';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';
import enUS from 'antd/lib/locale/en_US';
import { theme } from 'antd';

// 定义设置类型
export type ThemeType = 'light' | 'dark' | 'system';
export type LanguageType = 'zh_CN' | 'en_US';

interface SettingsContextType {
  themeMode: ThemeType;
  language: LanguageType;
  setThemeMode: (mode: ThemeType) => void;
  setLanguage: (lang: LanguageType) => void;
}

// 创建Context
export const SettingsContext = createContext<SettingsContextType>({
  themeMode: 'light',
  language: 'zh_CN',
  setThemeMode: () => {},
  setLanguage: () => {},
});

// Context Provider组件
export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 从localStorage读取保存的设置，如果没有则使用默认值
  const [themeMode, setThemeMode] = useState<ThemeType>(
    (localStorage.getItem('themeMode') as ThemeType) || 'light'
  );
  const [language, setLanguage] = useState<LanguageType>(
    (localStorage.getItem('language') as LanguageType) || 'zh_CN'
  );
  
  // 系统主题检测
  const [systemTheme, setSystemTheme] = useState<'light' | 'dark'>(
    window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  );

  // 监听系统主题变化
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? 'dark' : 'light');
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);
  
  // 当主题模式变化时，保存到localStorage
  useEffect(() => {
    localStorage.setItem('themeMode', themeMode);
  }, [themeMode]);
  
  // 当语言变化时，保存到localStorage
  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);
  
  // 根据主题模式和系统主题计算实际使用的主题
  const currentTheme = themeMode === 'system' ? systemTheme : themeMode;
  const { defaultAlgorithm, darkAlgorithm } = theme;
  
  // 应用主题到body元素
  useEffect(() => {
    if (currentTheme === 'dark') {
      document.body.setAttribute('data-theme', 'dark');
      document.documentElement.style.colorScheme = 'dark';
    } else {
      document.body.removeAttribute('data-theme');
      document.documentElement.style.colorScheme = 'light';
    }
  }, [currentTheme]);

  // 获取当前语言的locale配置
  const getLocale = () => {
    return language === 'en_US' ? enUS : zhCN;
  };
  
  // 为每个主题模式定义优化的颜色配置
  const getThemeConfig = () => {
    if (currentTheme === 'dark') {
      return {
        algorithm: darkAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          colorBgBase: '#141414',
          colorTextBase: 'rgba(255, 255, 255, 0.85)',
          colorBorder: '#303030',
        },
        components: {
          Menu: {
            colorItemBg: 'transparent',
            colorItemText: 'rgba(255, 255, 255, 0.85)',
          },
          Dropdown: {
            colorBgElevated: '#1f1f1f',
            colorText: 'rgba(255, 255, 255, 0.85)',
            boxShadowSecondary: '0 6px 16px 0 rgba(0, 0, 0, 0.65), 0 3px 6px -4px rgba(0, 0, 0, 0.72), 0 9px 28px 8px rgba(0, 0, 0, 0.65)',
          },
          Card: {
            colorBgContainer: '#1f1f1f',
            colorBorderSecondary: '#303030',
          },
          Select: {
            colorBgElevated: '#1f1f1f',
            colorText: 'rgba(255, 255, 255, 0.85)',
            colorTextPlaceholder: 'rgba(255, 255, 255, 0.45)',
            colorBgContainerDisabled: '#303030',
            colorTextDisabled: 'rgba(255, 255, 255, 0.25)',
          },
          List: {
            colorText: 'rgba(255, 255, 255, 0.85)',
            colorTextDescription: 'rgba(255, 255, 255, 0.45)',
            colorSplit: '#303030',
          },
          Collapse: {
            colorBgContainer: '#1f1f1f',
            colorText: 'rgba(255, 255, 255, 0.85)',
            colorBorder: '#303030',
            headerBg: '#1f1f1f',
            contentBg: '#141414',
            colorIcon: 'rgba(255, 255, 255, 0.65)',
            arrowColor: 'rgba(255, 255, 255, 0.65)',
          },
          Table: {
            colorBgContainer: '#1f1f1f',
            colorText: 'rgba(255, 255, 255, 0.85)',
            colorBorderSecondary: '#303030',
            colorTextHeading: 'rgba(255, 255, 255, 0.85)',
          },
          Input: {
            colorText: 'rgba(255, 255, 255, 0.85)',
            colorTextPlaceholder: 'rgba(255, 255, 255, 0.45)',
            colorBgContainer: '#1f1f1f',
            colorBorder: '#434343',
          },
          Modal: {
            colorBgElevated: '#1f1f1f',
            colorText: 'rgba(255, 255, 255, 0.85)',
          },
          Tag: {
            colorText: 'rgba(255, 255, 255, 0.85)',
            colorBorder: '#303030',
          }
        }
      };
    } else {
      return {
        algorithm: defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      };
    }
  };

  return (
    <SettingsContext.Provider
      value={{
        themeMode,
        language,
        setThemeMode,
        setLanguage,
      }}
    >
      <ConfigProvider
        locale={getLocale()}
        theme={getThemeConfig()}
      >
        {children}
      </ConfigProvider>
    </SettingsContext.Provider>
  );
};

// 自定义Hook，方便使用Context
export const useSettings = () => useContext(SettingsContext); 