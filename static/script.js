document.addEventListener("DOMContentLoaded", () => {
    let isSQLMode = true; // 初始模式为 SQL

    const chatForm = document.getElementById("chat-form");
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const toggleModeButton = document.getElementById("toggle-mode");
    const currentMode = document.getElementById("current-mode");
    const sampleQueryForm = document.getElementById("sample-query-form");
    const sampleTableSelect = document.getElementById("sample-table");
    const sampleQueriesDiv = document.getElementById("sample-queries");

    // 监听表单切换
    sampleTableSelect.addEventListener("change", (event) => {
        const selectedTable = event.target.value; // 获取当前选中的表名
        console.log(`Table switched to: ${selectedTable}`); // 调试输出

        // 根据新的表名加载样例查询
        loadSampleQueries(selectedTable);
    });

    let existingTables = [];

    // 动态加载表名列表
    const loadExistingTables = async () => {
        try {
            const response = await fetch('/get_tables');
            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }

            existingTables = data.tables || [];
            const tableDropdown = document.getElementById('sample-table');
            tableDropdown.innerHTML = ''; // 清空旧选项

            existingTables.forEach((table) => {
                const option = document.createElement('option');
                option.value = table;
                option.textContent = table;
                tableDropdown.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading tables:', error);
        }
    };

    // 上传文件逻辑
    const uploadForm = document.getElementById('upload-form');
    const submitButton = uploadForm.querySelector('button[type="submit"]');

    // 移除重复事件监听器（防止绑定多次）
    uploadForm.removeEventListener('submit', handleFileUpload);

    // 添加事件监听器
    uploadForm.addEventListener('submit', handleFileUpload);

    // 文件上传逻辑
    async function handleFileUpload(event) {
        event.preventDefault(); // 阻止表单默认提交行为

        const fileInput = document.getElementById('file-input');
        const tableNameInput = document.getElementById('table-name');
        const file = fileInput.files[0];
        const tableName = tableNameInput.value.trim();

        // 检查输入有效性
        if (!file || !tableName) {
            alert('Please select a file and enter a table name.');
            return;
        }

        // 检查表名格式是否有效
        const tableNamePattern = /^[a-zA-Z0-9_]+$/; // 仅允许字母、数字和下划线
        if (!tableNamePattern.test(tableName)) {
            alert("Invalid table name. Please use only letters, numbers, and underscores.");
            return;
        }

        // 检查表名是否存在
        if (!existingTables.map((table) => table.toLowerCase()).includes(tableName.toLowerCase())) {
            const confirmCreate = confirm(
                `The table "${tableName}" does not exist.\nDo you want to create it?`
            );
            if (!confirmCreate) {
                alert('Upload canceled.');
                return;
            }
        }

        // 禁用提交按钮，防止重复提交
        submitButton.disabled = true;

        // 准备上传数据
        const formData = new FormData();
        formData.append('file', file);
        formData.append('table_name', tableName);

        try {
            const response = await fetch('/upload_file', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (data.error) {
                console.error(`Upload error: ${data.error}`);
                alert(`Error uploading file: ${data.error}`);
            } else {
                alert(data.message);
                loadExistingTables(); // 上传成功后重新加载表名列表
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('An error occurred while uploading the file.');
        } finally {
            // 恢复提交按钮状态
            submitButton.disabled = false;
        }
    }


    // 页面加载时初始化表名列表
    document.addEventListener('DOMContentLoaded', loadExistingTables);

    /**
     * 动态加载表名逻辑
     */
    const loadTableNames = async () => {
        try {
            const response = await fetch("/get_tables");
            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }

            const sampleTableSelect = document.getElementById("sample-table");
            sampleTableSelect.innerHTML = ""; // 清空旧选项

            // 动态填充表名
            data.tables.forEach((table) => {
                const option = document.createElement("option");
                option.value = table;
                option.textContent = table;
                sampleTableSelect.appendChild(option);
            });

            // 默认加载第一个表的样例查询
            if (data.tables.length > 0) {
                loadSampleQueries(data.tables[0]);
            }
        } catch (error) {
            console.error("Error loading table names:", error);
            alert("Error: Unable to load table names.");
        }
    };


    const loadSampleQueries = async (tableName) => {
        try {
            const response = await fetch(`/generate_sample_queries?table_name=${tableName}`);
            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }

            const sampleQueriesDiv = document.getElementById("sample-queries");
            sampleQueriesDiv.innerHTML = ""; // 清空旧样例查询

            // 显示新的样例查询
            data.sample_queries.forEach((query) => {
                const queryDiv = document.createElement("div");
                queryDiv.textContent = query;
                sampleQueriesDiv.appendChild(queryDiv);
            });
        } catch (error) {
            console.error("Error loading sample queries:", error);
            alert("Error: Unable to generate sample queries.");
        }
    };


    // 监听下拉菜单切换事件
    document.getElementById("sample-table").addEventListener("change", (event) => {
        const tableName = event.target.value;
        loadSampleQueries(tableName);
    });

    // 加载样例查询
    sampleQueryForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const tableName = sampleTableSelect.value;
        if (!tableName) {
            alert("Please select a table.");
            return;
        }

        try {
            const response = await fetch(`/generate_sample_queries?table_name=${tableName}`);
            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                sampleQueriesDiv.innerHTML = ""; // 清空旧样例查询
                data.sample_queries.forEach((query) => {
                    const queryDiv = document.createElement("div");
                    queryDiv.textContent = query;
                    sampleQueriesDiv.appendChild(queryDiv);
                });
            }
        } catch (error) {
            alert("Error: Unable to generate sample queries.");
        }
    });

    // 页面加载时动态填充表名
    loadTableNames();

    /**
     * 逐字显示效果
     * @param {HTMLElement} element - 显示文本的目标元素
     * @param {string} text - 要显示的文本
     * @param {number} speed - 逐字显示速度（毫秒）
     * @param {number} chunkSize - 每次追加的字符数
     */
    const typeWriterEffect = (element, text, speed = 30, chunkSize = 10) => {
        let index = 0;

        const interval = setInterval(() => {
            if (index < text.length) {
                element.textContent += text.slice(index, index + chunkSize);
                index += chunkSize;
            } else {
                clearInterval(interval);
            }
        }, speed);
    };

    /**
     * 将数组数据渲染为 HTML 表格
     * @param {Array} data - JSON 数据数组
     * @returns {HTMLElement} - 表格元素
     */
    const renderResultAsTable = (data) => {
        const table = document.createElement("table");
        table.style.width = "100%";
        table.style.borderCollapse = "collapse";

        // 添加表头
        const headerRow = document.createElement("tr");
        Object.keys(data[0]).forEach((key) => {
            const th = document.createElement("th");
            th.textContent = key;
            th.style.border = "1px solid #ddd";
            th.style.padding = "8px";
            th.style.background = "#f1f1f1";
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        // 添加表格内容
        data.forEach((row) => {
            const tr = document.createElement("tr");
            Object.values(row).forEach((value) => {
                const td = document.createElement("td");
                td.textContent = value;
                td.style.border = "1px solid #ddd";
                td.style.padding = "8px";
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        return table;
    };

    /**
     * 添加消息到聊天框
     * @param {string | Array} message - 消息内容，字符串或数组
     * @param {boolean} isUser - 是否为用户消息
     */
    const addMessage = (message, isUser = true) => {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", isUser ? "user-message" : "bot-message");

        if (!isUser && Array.isArray(message)) {
            // 渲染为表格
            const table = renderResultAsTable(message);
            messageDiv.appendChild(table);
        } else if (!isUser) {
            // 渲染逐字显示文本
            typeWriterEffect(messageDiv, message);
        } else {
            messageDiv.textContent = message;
        }

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // 滚动到最新消息
    };

    /**
     * 切换模式逻辑
     */
    toggleModeButton.addEventListener("click", () => {
        isSQLMode = !isSQLMode; // 切换模式
        currentMode.textContent = `Mode: ${isSQLMode ? "SQL" : "NoSQL"}`;
        toggleModeButton.textContent = `Switch to ${isSQLMode ? "NoSQL" : "SQL"}`;
    });

    /**
     * 处理用户输入和服务器交互
     */
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const userMessage = userInput.value.trim();
        if (!userMessage) return;

        // 显示用户输入
        addMessage(userMessage, true);
        userInput.value = "";

        // 根据当前模式选择 API
        const endpoint = isSQLMode ? "/execute_query" : "/execute_nosql_query";

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: userMessage }),
            });

            const data = await response.json();

            if (data.error) {
                addMessage(`Error: ${data.error}`, false);
            } else {
                addMessage(`Query: ${data.query}`, false);
                if (Array.isArray(data.result) && data.result.length > 0) {
                    addMessage(data.result, false); // 渲染为表格
                } else {
                    addMessage("No results found.", false);
                }
            }
        } catch (error) {
            addMessage("Error: Unable to connect to the server.", false);
        }
    });
});
