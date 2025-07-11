# 📋 US-001 Installation Checklist

**Epic**: 1 - Proof of Concept  
**User Story**: US-001 - Local LLM Setup  
**Target Server**: CentOS 8 (IP: 10.14.190.5)  
**Date Started**: 2025-07-09 15:30:00  
**Date Completed**: _____________  

---

## 🎯 Installation Progress

### ⏳ **Status Legend:**
- [ ] ⏳ Not Started
- [ ] 🔄 In Progress  
- [ ] ✅ Completed Successfully
- [ ] ❌ Failed (needs attention)

---

## 🔧 **Pre-Installation Checklist**

### **System Requirements:**
- [x] ✅ CentOS 8 server available
- [x] ✅ SSH access with private key
- [x] ✅ Server specs: 16+ GB RAM, 20+ GB disk
- [x] ✅ Internet connectivity on server
- [x] ✅ Root or sudo privileges

### **Client Requirements:**
- [x] ✅ SSH client available
- [x] ✅ Private key file accessible
- [x] ✅ Deployment scripts prepared

---

## 🚀 **Installation Steps**

### **Step 1: User Management**
- [x] ✅ Check if ollama user exists
- [x] ✅ Create ollama system user if needed
- [x] ✅ Verify user creation

**Commands:**
```bash
id ollama || useradd -r -s /bin/false -d /opt/ollama ollama
```

**Validation:**
```bash
id ollama
```
**Expected Output:**
- Nếu user tồn tại: in ra thông tin user ollama (uid, gid, group).
- Nếu user không tồn tại: không in ra gì hoặc báo lỗi "no such user".

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-09 15:35:00  
**Notes**: Ollama user created successfully

---

### **Step 2: Directory Setup**
- [x] ✅ Create /opt/ollama directory
- [x] ✅ Set proper ownership to ollama user
- [x] ✅ Verify directory permissions

**Commands:**
```bash
mkdir -p /opt/ollama && chown ollama:ollama /opt/ollama
```

**Validation:**
```bash
[ -d /opt/ollama ] && [ $(stat -c %U /opt/ollama) = 'ollama' ]
```
**Expected Output:**
- Không in ra gì, mã thoát = 0 nếu thư mục tồn tại và owner là ollama.
- Nếu không đúng, mã thoát ≠ 0.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-09 15:40:00  
**Notes**: Directory created with proper permissions

---

### **Step 3: Ollama Binary Installation**
- [x] ✅ Download Ollama binary from GitHub
- [x] ✅ Extract .tgz archive
- [x] ✅ Make binary executable
- [x] ✅ Move to /usr/local/bin/
- [x] ✅ Verify installation and version

**Commands:**
```bash
# Giải nén file ollama-linux-amd64.tgz
cd ~/Downloads
 tar -xzf ollama-linux-amd64.tgz
# Di chuyển và cấp quyền thực thi
sudo mv ollama /usr/local/bin/ollama
sudo chmod +x /usr/local/bin/ollama
```

**Validation:**
```bash
[ -f /usr/local/bin/ollama ] && /usr/local/bin/ollama --version
```
**Expected Output:**
- In ra version của ollama nếu cài đặt thành công.
- Nếu không có file hoặc lỗi, không in ra version, mã thoát ≠ 0.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-09 16:20:00  
**Notes**: Đã giải nén file .tgz, di chuyển và cấp quyền thực thi cho binary ollama

---

### **Step 4: Systemd Service Creation**
- [x] ✅ Create ollama.service file
- [x] ✅ Configure service parameters
- [x] ✅ Set environment variables
- [x] ✅ Verify service file exists

**Service Configuration:**
```ini
\[Unit\]
Description=Ollama Service
After=network.target

\[Service\]
Type=simple
User=ollama
Group=ollama
WorkingDirectory=/opt/ollama
ExecStart=/usr/local/bin/ollama serve
Environment=OLLAMA_HOST=0.0.0.0:11434
Environment=OLLAMA_ORIGINS=*
Restart=always
RestartSec=3

\[Install\]
WantedBy=multi-user.target
```

**Validation:**
```bash
[ -f /etc/systemd/system/ollama.service ]
```
**Expected Output:**
- Không in ra gì, mã thoát = 0 nếu file tồn tại.
- Nếu không có file, mã thoát ≠ 0.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-09 16:00:00  
**Notes**: Service file created with correct configuration

---

### **Step 5: Service Enablement**
- [x] ✅ Reload systemd daemon
- [x] ✅ Enable ollama service for auto-start
- [x] ✅ Verify service is enabled

**Commands:**
```bash
systemctl daemon-reload && systemctl enable ollama
```

**Validation:**
```bash
systemctl is-enabled ollama
```
**Expected Output:**
- In ra "enabled" nếu service đã enable thành công.
- Nếu chưa enable, in ra "disabled" hoặc báo lỗi.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-09 16:05:00  
**Notes**: Service enabled and daemon reloaded successfully

---

### **Step 6: Service Startup**
- [x] ✅ Start ollama service
- [x] ✅ Verify service starts without errors  
- [x] ✅ Check initial service status

**Commands:**
```bash
systemctl start ollama
```

**Validation:**
```bash
systemctl is-active ollama
```
**Expected Output:**
- In ra "active" nếu service đang chạy.
- Nếu không chạy, in ra "inactive", "failed" hoặc trạng thái khác.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-09 16:30:00  
**Notes**: Dịch vụ ollama đã active, khởi động thành công

---

### **Step 7: Service Health Check**
- [x] ✅ Wait for service to be fully ready
- [x] ✅ Monitor service status for 30 seconds
- [x] ✅ Verify service is stable and running

**Wait Time**: 30 seconds maximum  
**Check Interval**: 1 second  

**Validation:**
```bash
systemctl is-active --quiet ollama
```
**Expected Output:**
- Lệnh không in ra gì nếu dịch vụ đang chạy (active), mã thoát (exit code) = 0.
- Nếu dịch vụ không chạy (inactive/failed), lệnh cũng không in ra gì, mã thoát ≠ 0.
- Kiểm tra mã thoát bằng: `echo $?` (0 = active, khác 0 = không active)

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-09 17:00:00  
**Notes**: Dịch vụ ollama ổn định, health check thành công

---

### **Step 8: Firewall Configuration**
- [x] ✅ Add port 11434 to firewall
- [x] ✅ Make firewall rule permanent
- [x] ✅ Reload firewall configuration
- [x] ✅ Verify port is open

**Commands:**
```bash
firewall-cmd --permanent --add-port=11434/tcp && firewall-cmd --reload
```

**Validation:**
```bash
firewall-cmd --list-ports | grep -q 11434
```
**Expected Output:**
- Không in ra gì, mã thoát = 0 nếu port 11434 đã mở.
- Nếu chưa mở, mã thoát ≠ 0.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-10 09:37:35  
**Notes**: Port 11434 đã mở, firewall reload thành công

---

### **Step 9: API Endpoint Testing**
- [x] ✅ Test connection to Ollama API
- [x] ✅ Verify API responds correctly
- [x] ✅ Check API returns expected JSON format

**Commands:**
```bash
curl -s http://localhost:11434/api/tags
```

**Validation:**
```bash
curl -s http://localhost:11434/api/tags | grep -q models
```
**Expected Output:**
- Không in ra gì, mã thoát = 0 nếu API trả về JSON có trường "models".
- Nếu không đúng, mã thoát ≠ 0.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-10 09:37:38  
**Notes**: API trả về kết quả đúng định dạng, đã kiểm tra thành công

---

### **Step 10: Model Download**
- [x] ✅ Download Mistral 7B model
- [x] ✅ Wait for download completion (several minutes)
- [x] ✅ Verify model is available

**Commands:**
```bash
ollama pull mistral:7b
```

**Validation:**
```bash
ollama list | grep -q mistral
```
**Expected Output:**
- Không in ra gì, mã thoát = 0 nếu model mistral đã có trong danh sách.
- Nếu chưa có, mã thoát ≠ 0.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-10 10:45:00  
**Notes**: Model Mistral 7B đã tải và sẵn sàng sử dụng

---

### **Step 11: Model Response Testing**
- [x] ✅ Test model with sample query
- [x] ✅ Verify model responds appropriately
- [x] ✅ Check response quality

**Commands:**
```bash
echo 'Hello, can you respond?' | ollama run mistral:7b
```

**Test Query**: "Hello, can you respond?"  
**Expected**: Coherent response in English  
**Expected Output:**
- In ra câu trả lời hợp lý bằng tiếng Anh từ model.
- Nếu không có phản hồi hoặc lỗi, không in ra gì hoặc báo lỗi.

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-10 10:50:00  
**Notes**: Model phản hồi tốt, kiểm tra chất lượng thành công

---

### **Step 12: Health Check Script Creation**
- [x] ✅ Create comprehensive health check script
- [x] ✅ Make script executable
- [x] ✅ Test health check functionality
- [x] ✅ Verify all components are working

**Script Location**: `/usr/local/bin/ollama_health_check.sh`

**How to create the script (nếu cài thủ công):**
```bash
sudo tee /usr/local/bin/ollama_health_check.sh > /dev/null <<'EOF'
#!/bin/bash
OLLAMA_HOST="localhost:11434"
MODEL_NAME="mistral:7b"
if ! systemctl is-active ollama &>/dev/null; then
    echo "❌ Ollama service is not running"
    exit 1
fi
if ! curl -s "http://$OLLAMA_HOST/api/tags" > /dev/null; then
    echo "❌ Ollama API is not responding"
    exit 1
fi
if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "❌ Model $MODEL_NAME is not available"
    exit 1
fi
TEST_QUERY="Test query"
RESPONSE=$(timeout 30 ollama run "$MODEL_NAME" "$TEST_QUERY" 2>/dev/null)
if [[ -n "$RESPONSE" ]]; then
    echo "✅ Ollama is healthy"
    echo "   - Service: Running"
    echo "   - API: Responding"
    echo "   - Model: $MODEL_NAME available"
    echo "   - Response time: <30 seconds"
    exit 0
else
    echo "❌ Model is not responding properly"
    exit 1
fi
EOF
sudo chmod +x /usr/local/bin/ollama_health_check.sh
```

**Commands:**
```bash
/usr/local/bin/ollama_health_check.sh
```
**Validation:**
- Chạy script, kiểm tra các dòng trạng thái trả về
**Expected Output:**
- In ra "✅ Ollama is healthy" nếu mọi thành phần đều hoạt động
- Nếu có lỗi, in ra thông báo tương ứng (service, API, model, response)

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-10 14:52:50  
**Notes**: Script health check đã tạo, kiểm tra thành công

---

## 🏁 **Final Verification**

### **Complete System Test:**
- [x] ✅ Run comprehensive health check
- [x] ✅ Test Vietnamese language query
- [x] ✅ Test English language query
- [x] ✅ Verify performance metrics

### **Vietnamese Test:**
```bash
ollama run mistral:7b "Xin chào, bạn có thể trả lời bằng tiếng Việt không?"
```

### **English Test:**
```bash
ollama run mistral:7b "Hello, can you help me with questions in English?"
```

### **Performance Check:**
- [x] ✅ Response time < 15 seconds
- [x] ✅ Memory usage reasonable
- [x] ✅ Service stable after restart

**Status**: ✅ Completed Successfully  
**Completed**: 2025-07-10 14:52:50  
**Notes**: Đã kiểm tra toàn bộ hệ thống, mọi chức năng hoạt động ổn định

---

## 📊 **Installation Summary**

**Total Steps**: 12 + Final Verification  
**Steps Completed**: 13 / 12  
**Overall Status**: ✅ Completed Successfully

**Installation Start Time**: 2025-07-10 09:37:35  
**Installation End Time**: 2025-07-10 14:52:50  
**Total Duration**: 5h 15m  

**Final Health Check Result**: ✅ All systems healthy

---

## 🔗 **Post-Installation**

### Documentation Updates:
- [x] ✅ Update Epic 1 status to "US-001 Complete"
- [x] ✅ Record server configuration details
- [x] ✅ Document any deviations or issues
- [x] ✅ Prepare handover notes for US-002

### Team Notification:
- [x] ✅ Inform development team
- [x] ✅ Share server access details (secure)
- [x] ✅ Schedule US-002 planning meeting

**Completed By**: AnhLH48  
**Verified By**: AnhLH48  
**Sign-off Date**: 2025-07-10 14:52:50

---

**Next Step**: Begin US-002 - Document Processing Pipeline 