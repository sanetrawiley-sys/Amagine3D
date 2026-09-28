import styles from './LeftPanel.module.css';
import { ChatPanel, type ChatPanelProps } from './ChatPanel';
import { FilesPanel, type FilesPanelProps } from './FilesPanel';
import type { Language, LeftView } from './types';
import { translator } from './types';

interface LeftPanelProps {
  chat: ChatPanelProps;
  collapsed: boolean;
  files: FilesPanelProps;
  language: Language;
  onToggleCollapsed: () => void;
  onViewChange: (view: LeftView) => void;
  view: LeftView;
}

export function LeftPanel({
  chat,
  collapsed,
  files,
  language,
  onToggleCollapsed,
  onViewChange,
  view,
}: LeftPanelProps) {
  const text = translator(language);
  return (
    <aside
      aria-label={text('Conversation and generated files', '对话与生成文件')}
      className={`${styles.leftPanel} ${collapsed ? styles.collapsedPanel : ''}`}
    >
      <header className={styles.panelHeader}>
        {collapsed ? null : (
          <div
            aria-label={text('Left panel view', '左侧面板视图')}
            className={styles.leftTabs}
            role="tablist"
          >
            <button
              aria-selected={view === 'chat'}
              onClick={() => onViewChange('chat')}
              role="tab"
              type="button"
            >
              {text('Chat', '对话')}
            </button>
            <button
              aria-selected={view === 'files'}
              onClick={() => onViewChange('files')}
              role="tab"
              type="button"
            >
              {text('Files', '文件')}
            </button>
          </div>
        )}
        <div className={styles.panelControls}>
          <button
            aria-expanded={!collapsed}
            aria-label={text('Toggle conversation panel', '切换对话面板')}
            className={styles.panelCollapseButton}
            onClick={onToggleCollapsed}
            type="button"
          >
            {collapsed ? '›' : '‹'}
          </button>
        </div>
      </header>

      {collapsed ? null : view === 'chat' ? (
        <ChatPanel {...chat} />
      ) : (
        <FilesPanel {...files} />
      )}
    </aside>
  );
}
