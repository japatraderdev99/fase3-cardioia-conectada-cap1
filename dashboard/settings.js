module.exports = {
 uiHost: '127.0.0.1', uiPort: 1887,
 flowFile: 'flows.json',
 editorTheme: { projects: { enabled: false } },
 logging: { console: { level: 'info', metrics: false, audit: false } },
 contextStorage: { default: { module: 'memory' } }
};
