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
    const constructSelect = document.getElementById("construct-select");  // 新增选择语言结构的下拉菜单
    const generateConstructButton = document.getElementById("generate-construct");
    
    toggleModeButton.addEventListener("click", () => {
        isSQLMode = !isSQLMode; // 切换模式
        currentMode.textContent = `Mode: ${isSQLMode ? "SQL" : "NoSQL"}`;
        toggleModeButton.textContent = `Switch to ${isSQLMode ? "NoSQL" : "SQL"}`;

        // 动态加载模式特定的数据（表名或集合）
        loadTableNames();
    });

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
        const endpoint = isSQLMode ? "/get_tables" : "/mongo/explore"; // 根据模式选择 API
        try {
            const response = await fetch(endpoint);
            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }

            const sampleTableSelect = document.getElementById("sample-table");
            sampleTableSelect.innerHTML = ""; // 清空旧选项

            const items = isSQLMode ? data.tables : Object.keys(data); // SQL: tables, NoSQL: collections
            items.forEach((item) => {
                const option = document.createElement("option");
                option.value = item;
                option.textContent = item;
                sampleTableSelect.appendChild(option);
            });
        } catch (error) {
            console.error(`Error loading ${isSQLMode ? "tables" : "collections"}:`, error);
        }
    };


    // 更新 loadSampleQueries 函数，只显示当前选中表格的信息
    const loadSampleQueries = async (tableName) => {
        // 判断是否为 SQL 模式，构建 API 路径
        const endpoint = isSQLMode
            ? `/get_table_info?table_name=${tableName}`
            : `/mongo/get_collection_info?collection_name=${tableName}`; // 区分 SQL 和 NoSQL

        try {
            // 请求表格信息
            const response = await fetch(endpoint);
            const data = await response.json();

            // 如果后端返回错误
            if (data.error) {
                addMessage(`Error: ${data.error}`, false); // 显示错误消息到聊天框
                return;
            }

            // 显示表格信息（列名和类型）
            if (data.columns) {
                let columnsInfo = `Selected Table: ${tableName}\nColumns:\n`;
                data.columns.forEach((col) => {
                    columnsInfo += `- ${col.name} (${col.type})\n`;
                });
                addMessage(columnsInfo, false);
            }

            // 显示表格的示例数据
            if (data.sample_data && data.sample_data.length > 0) {
                let sampleDataInfo = "Sample Data:\n";
                data.sample_data.forEach((row, index) => {
                    sampleDataInfo += `Row ${index + 1}: ${JSON.stringify(row)}\n`;
                });
                addMessage(sampleDataInfo, false);
            } else {
                addMessage(`No sample data available for table: ${tableName}`, false);
            }
        } catch (error) {
            console.error("Error loading table information:", error);
            addMessage("Error: Unable to load table information.", false);
        }
    };

    // 监听下拉菜单切换事件，只加载当前选中表格
    document.getElementById("sample-table").addEventListener("change", async (event) => {
        const tableName = event.target.value; // 获取当前选中的表格名称
        if (tableName) {
            addMessage(`Switching to table: ${tableName}`, false); // 提示用户切换表格// 加载并显示当前表格信息
        }
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
        const endpoint = isSQLMode ? "/execute_query" : "/mongo/natural_language_query";

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
                // 显示自然语言描述
                addMessage(`Description: ${data.description}`, false);

                // 显示查询内容
                addMessage(`Query: ${data.query}`, false);

                // 显示查询结果
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

    // 监听下拉菜单的切换
    constructSelect.addEventListener("change", async () => {
        const tableName = sampleTableSelect.value; // 获取当前选中的表名
        const construct = constructSelect.value; // 获取当前选中的查询类型

        if (!tableName || !construct) {
            sampleQueriesDiv.innerHTML = `<p>Please select a table and a query type.</p>`;
            return;
        }

        // 清空旧内容
        sampleQueriesDiv.innerHTML = "";

        const allQueries = []; // 用于存储所有查询结果

        try {
            // 每次切换时发送 3 次请求
            for (let i = 0; i < 3; i++) {
                const endpoint = `/generate_construct_queries?table_name=${tableName}&construct=${construct}`;
                const response = await fetch(endpoint);
                const data = await response.json();

                // 处理后端返回结果
                if (data.error) {
                    allQueries.push({ query: null, description: `Error: ${data.error}` });
                    break;
                } else {
                    allQueries.push({ query: data.query, description: data.description });
                }
            }

            // 显示所有查询结果
            allQueries.forEach((item, index) => {
                if (item.query) {
                    sampleQueriesDiv.innerHTML += `
                        <pre>Query ${index + 1}: ${item.query}</pre>
                        <p>Description: ${item.description}</p>
                    `;
                } else {
                    sampleQueriesDiv.innerHTML += `
                        <p>${item.description}</p>
                    `;
                }
            });
        } catch (error) {
            console.error("Error generating query:", error);
            sampleQueriesDiv.innerHTML = `<p>Failed to generate query.</p>`;
        }
    });



        // 监听生成特定语言结构查询的点击事件
    generateConstructButton.addEventListener("click", async () => {
        const tableName = sampleTableSelect.value;
        const construct = constructSelect.value; // 获取选定的语言结构

        if (!tableName || !construct) {
            alert("Please select a table and a construct type.");
            return;
        }

        try {
            const response = await fetch(`/generate_construct_queries?table_name=${tableName}&construct=${construct}`);
            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                const sampleQueriesDiv = document.getElementById("sample-queries");
                sampleQueriesDiv.innerHTML = `<pre>${data.query}</pre>`;
            }
        } catch (error) {
            console.error("Error generating construct query:", error);
        }
    });

    document.getElementById("sample-query-form").addEventListener("submit", async (e) => {
        e.preventDefault();

        const tableName = document.getElementById("sample-table").value;
        const construct = document.getElementById("construct-select").value;

        if (!tableName || !construct) {
            alert("Please select a table/collection and a query type.");
            return;
        }

        const endpoint = isSQLMode
            ? `/generate_construct_queries?table_name=${tableName}&construct=${construct}`
            : `/mongo/sample_queries`; // MongoDB 暂无构造逻辑，调用示例查询

        try {
            const response = await fetch(endpoint);
            const data = await response.json();

            const sampleQueriesDiv = document.getElementById("sample-queries");
            sampleQueriesDiv.innerHTML = "";

            if (data.error) {
                sampleQueriesDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            } else if (isSQLMode) {
                sampleQueriesDiv.innerHTML = `<pre>${data.query}</pre>`;
            } else {
                data.forEach((query) => {
                    const queryDiv = document.createElement("div");
                    queryDiv.textContent = `${query.description}: ${query.query}`;
                    sampleQueriesDiv.appendChild(queryDiv);
                });
            }
        } catch (error) {
            console.error("Error fetching sample queries:", error);
        }
    });


    document.getElementById("chat-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const userMessage = document.getElementById("user-input").value.trim(); // 获取用户输入
        const selectedCollection = document.getElementById("sample-table").value; // 获取选中的集合名

        if (!userMessage || !selectedCollection) {
            alert("Please enter a query and select a collection.");
            return;
        }

        console.log("Query:", userMessage);
        console.log("Collection:", selectedCollection);

        const endpoint = "/mongo/natural_language_query";
        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: userMessage, // 自然语言或 MongoDB 查询
                    collection: selectedCollection, // 集合名
                }),
            });

            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                console.log("Response:", data);
            }
        } catch (error) {
            console.error("Error connecting to server:", error);
        }
    });




});
