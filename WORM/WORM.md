# << 簡易網路蠕蟲 - 字典攻擊 >>

### 功能

* isInfectedSystem( sftpClient ) : 
    << 返回蠕蟲是否應該傳播 >>
        &emsp;&emsp;檢查系統是否被感染。 一種方法是檢查目錄 /tmp 中名為 infected.txt 的文件（您在將系統標記為受感染時創建的文件）。
<br/>

* markInfected( ) :
    << 將系統標記為已感染 >>
        &emsp;&emsp;將系統標記為已感染。 一種方法是在目錄 /tmp/ 中創建一個名為 infected.txt 的文件。
<br/>

* spreadAndExecute( sshClient, sftpClient ) :
    << 傳播到其他系統並執行 >>
        &emsp;&emsp;此函數將 SSH 類的實例作為參數，該實例已正確初始化並連接到受害系統。 蠕蟲會將自身複製到遠程系統，將其權限更改為可執行文件，然後執行自身。 請查看我們用於課堂練習的代碼。 進入此函數的代碼與該代碼非常相似。
<br/>

* tryCredentials( host, userName, password, sshClient ) :
    << 嘗試連接到給定主機與給定現有cred >>
        &emsp;&emsp;嘗試使用存儲在變量 userName 中的用戶名和存儲在變量 password 中的密碼以及 SSH 類 sshClient 的實例連接到主機主機。
<br/>

* attackSystem( host ) :
    << 對主機發起字典攻擊 >>
        &emsp;&emsp;
<br/>

* getMyIP( interface ) :
    << 返回當前系統的IP >>
        &emsp;&emsp;
<br/>

* getHostsOnTheSameNetwork( ) :
    << 返回同一網絡上的系統列表 >>
        &emsp;&emsp;
<br/>

* clean_mess( sshClient, sftpClient ) :
    << 檢查系統是否被感染，如果被感染則執行清理 >>
        &emsp;&emsp;
<br/>

* find_file( file_name ) :
    << 返回worm.py所在的文件路徑，如未找到返回None >>
        &emsp;&emsp;
<br/>

* 默認功能
    