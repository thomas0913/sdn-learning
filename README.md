# << OF-RHM策略應用蠕蟲防禦之實作 >>

### [ 動機 ]
<p>
    &emsp;&emsp;電腦蠕蟲為一種具有破壞性的自我複製程序，一旦進入計算機或網絡，就會透過刪除、修改、分發或以其他方式操縱數據，例如2017年WannaCry蠕蟲，結至2018有至少有150個國家在同一時間遭到攻擊。
</p>
<strong>
    &emsp;&emsp; ===>>> &emsp;電腦蠕蟲的散播性與多變性，讓全球資訊安全受到威脅。
</strong>

### [ 目的 ]
<p>
    &emsp;&emsp;藉由軟體定義網路(SDN)架構，利用OpenFlow協議之" 隨機主機變換 "之策略演算法，
    以有效預防電腦蠕蟲之網路傳播。
</p>

### [ 實作方法 ]

- 實作步驟 :
    1. 建構簡易 Ryu App，並測試TCP數據傳輸之可行性。
    2. 參考[Moving Target Defense using Software Defined Networking](https://github.com/girishsg24/Moving-Target-Defense-RHM-using-SDN)之文章，實作出OF-RHM控制器。
    3. 實作並撰寫簡單版本之網路電腦蠕蟲。
    4. 整合測試並驗證。

### [ 參考資料 ]

* [http://mininet.org/](http://mininet.org/)
* [https://ryu.readthedocs.io/en/latest/getting_started.html](https://ryu.readthedocs.io/en/latest/getting_started.html)
* [https://github.com/girishsg24/Moving-Target-Defense-RHM-using-SDN](https://github.com/girishsg24/Moving-Target-Defense-RHM-using-SDN)
* [https://dl.acm.org/doi/10.1145/2342441.2342467](https://dl.acm.org/doi/10.1145/2342441.2342467)
* [https://osrg.github.io/ryu-book/en/html/switching_hub.html](https://osrg.github.io/ryu-book/en/html/switching_hub.html)
* [https://blog.downager.com/2013/07/03/%E7%B6%B2%E8%B7%AF-%E6%B7%BA%E8%AB%87-ARP-Address-Resolution-Protocol-%E9%81%8B%E4%BD%9C%E5%8E%9F%E7%90%86/](https://blog.downager.com/2013/07/03/%E7%B6%B2%E8%B7%AF-%E6%B7%BA%E8%AB%87-ARP-Address-Resolution-Protocol-%E9%81%8B%E4%BD%9C%E5%8E%9F%E7%90%86/)
* [http://www.tsnien.idv.tw/Internet_WebBook/chap5/5-4%20ICMP%20%E9%80%9A%E8%A8%8A%E5%8D%94%E5%AE%9A.html](http://www.tsnien.idv.tw/Internet_WebBook/chap5/5-4%20ICMP%20%E9%80%9A%E8%A8%8A%E5%8D%94%E5%AE%9A.html)
* [https://tingkuan.wordpress.com/2018/04/12/%E3%80%90ryu-controller-%E9%81%8B%E4%BD%9C%E5%8E%9F%E7%90%86%E3%80%91/](https://tingkuan.wordpress.com/2018/04/12/%E3%80%90ryu-controller-%E9%81%8B%E4%BD%9C%E5%8E%9F%E7%90%86%E3%80%91/)
* [https://github.com/pylyf/NetWorm](https://github.com/pylyf/NetWorm)