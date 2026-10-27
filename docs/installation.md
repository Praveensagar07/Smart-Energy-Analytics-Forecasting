# Installation & Environment Configuration Guide

## Smart Energy Consumption Analytics & Forecasting
**Target Platforms**: Windows 11 / WSL2 (Ubuntu 22.04 LTS)  
**System Constraints**: 8 GB RAM, Sequential Execution Architecture

---

## 1. System Requirements & Prerequisites

| Component | Minimum Specification | Recommended Specification | Configured Environment |
|---|---|---|---|
| Operating System | Windows 10/11 (64-bit) or Ubuntu 20.04+ | Windows 11 64-bit | Windows 11 Pro |
| Processor | 4 Cores | 8 Cores (Intel i5-1335U) | 10 Cores (Intel Core i5-1335U) |
| RAM | 8 GB | 16 GB | 8 GB (Sequential execution optimized) |
| Disk Storage | 5 GB free disk space | 20 GB SSD | 150+ GB SSD available |
| Java Runtime | OpenJDK 11 | OpenJDK 17 LTS | Microsoft OpenJDK 17.0.14 LTS |
| Python | Python 3.9 – 3.12 | Python 3.11 / 3.12 | Python 3.13.9 (Anaconda3) |
| Big Data Stack | PySpark 3.5+ | PySpark 4.0+ & Hadoop 3.3+ | PySpark 4.0.1 & Hadoop Winutils 3.3.6 |

---

## 2. Windows Native Environment Setup

### Step 1: Clone Repository
```powershell
git clone https://github.com/Praveensagar07/Smart-Energy-Analytics-Forecasting.git
cd Smart-Energy-Analytics-Forecasting
```

### Step 2: Configure Python Dependencies
Install required packages using Anaconda or standard pip:
```powershell
pip install -r requirements.txt
```

Verify installed packages:
```powershell
python -c "import pandas, numpy, sklearn, matplotlib, seaborn, pyspark, pytest; print('Dependencies verified!')"
```

### Step 3: Install Java Development Kit (OpenJDK 17 LTS)
PySpark and Hadoop require a 64-bit Java Runtime Environment:
1. Download Microsoft OpenJDK 17 zip:
   ```powershell
   # Automated extraction into user directory
   Invoke-WebRequest -Uri "https://aka.ms/download-jdk/microsoft-jdk-17.0.14-windows-x64.zip" -OutFile "$HOME\jdk-17.zip"
   Expand-Archive -Path "$HOME\jdk-17.zip" -DestinationPath "$HOME\jdk-17"
   ```
2. Configure Environment Variables:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("JAVA_HOME", "$HOME\jdk-17\jdk-17.0.14+7", "User")
   $env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
   ```
3. Verify Java installation:
   ```powershell
   java -version
   ```

### Step 4: Configure Windows Native Hadoop Binaries (Winutils)
Native Windows execution of Spark/Hadoop requires `winutils.exe` and `hadoop.dll`:
```powershell
New-Item -ItemType Directory -Force -Path "C:\hadoop\bin"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.6/bin/winutils.exe" -OutFile "C:\hadoop\bin\winutils.exe"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.6/bin/hadoop.dll" -OutFile "C:\hadoop\bin\hadoop.dll"

# Set HADOOP_HOME
[System.Environment]::SetEnvironmentVariable("HADOOP_HOME", "C:\hadoop", "User")
$env:PATH = "C:\hadoop\bin;$env:PATH"
```

---

## 3. WSL2 / Linux Hadoop Single-Node Setup (Optional for Multi-Node Cluster)

For academic lab setups running a complete native Linux Hadoop ecosystem:

```bash
# 1. Update and install Java
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk ssh pdsh

# 2. Download and configure Apache Hadoop 3.3.6
wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
sudo tar -xzf hadoop-3.3.6.tar.gz -C /usr/local/
sudo mv /usr/local/hadoop-3.3.6 /usr/local/hadoop

# 3. Configure ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export HADOOP_HOME=/usr/local/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
source ~/.bashrc

# 4. Format and Start HDFS
hdfs namenode -format
start-dfs.sh
start-yarn.sh

# 5. Verify Active Daemons
jps
# Should list: NameNode, DataNode, SecondaryNameNode, ResourceManager, NodeManager
```

---

## 4. Verification Check

Run the automated diagnostic tool to verify all tooling:
```powershell
python scripts/verify_environment.py
```
Expected output:
- `OS Platform`: Windows 11
- `Java Version`: openjdk version "17.0.14" [FOUND]
- `Winutils Binary`: C:\hadoop\bin\winutils.exe [FOUND]
- `PySpark Library`: v4.0.1 [INSTALLED]
