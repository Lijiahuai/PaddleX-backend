# run.py

from App import create_app

# 创建 Flask 应用实例
app = create_app()

if __name__ == '__main__':
    # 启动应用
    app.run(host='0.0.0.0', port=5600, debug=app.config['DEBUG'])


