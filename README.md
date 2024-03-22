## OpenOPC_Py38
=======

### 使用说明：
1. 使用前，需要在管理员cmd中注册 openopc/lib/gbda_aut.dll 库文件，否则无法使用
- 注册=regsvr32 gbda_aut.dll
- 卸载=regsvr32 -u gbda_aut.dll

2. 本版本1.4.0,在使用 OPenOPCService.exe 时，若需修改默认的参数，是需要通过环境变量来修改的
- 主要添加如下变量：
  - OPC_CLASS=Matrikon.OPC.Automation;Graybox.OPC.DAWrapper;HSCOPC.Automation;RSI.OPCAutomation;OPC.Automation
  - OPC_CLIENT=OpenOPC
  - OPC_GATE_HOST=0.0.0.0
  - OPC_GATE_PORT=7766
  - OPC_HOST=localhost
  - OPC_INACTIVE_TIMEOUT=60 
  - OPC_MAX_CLIENTS=25
  - OPC_MODE=dcom
  - OPC_SERVER=Hci.TPNServer;HwHsc.OPCServer;opc.deltav.1;AIM.OPC.1;Yokogawa.ExaopcDAEXQ.1;OSI.DA.1;OPC.PHDServerDA.1;Aspen.Infoplus21_DA.1;National Instruments.OPCLabVIEW;RSLinx OPC Server;KEPware.KEPServerEx.V4;KEPware.KEPServerEx.V6;Matrikon.OPC.Simulation;Prosys.OPC.Simulation
### 使用OPenOPCService,也就是RMI服务
使用 OPenOPCService.exe 可安装为 windows 服务使用
- 如 cmd 下输入：
  - 安装=OPenOPCService.exe install
  - 卸载=OPenOPCService.exe remove
  - 停止=OPenOPCService.exe stop
  - 启动=OPenOPCService.exe start
  - 重启=OPenOPCService.exe restart

### 使用HTTP Gateway服务
要使用HTTP Gateway,需要开启两项服务，分别是`OpenOPC_Py38\bin\OpenOPCNameService.exe`与`OpenOPC_Py38\bin\StartHttpGateway.exe`
- 同使用OPenOPCService一样，OpenOPCNameService也需要注册成windows服务
- 注册OpenOPCNameService服务后，开启StartHttpGateway(直接运行即可)

### 更多说明可见：
[更多说明,见这里](https://github.com/YQBaobao/openopc-python3.8/blob/master/OpenOPC_Py38/bin/readme.md)

### 配套的示例客户端
[示例客户端仓库](https://github.com/YQBaobao/openopc-client)

## 以下为原 readme.txt 内容：

OpenOPC for Python 3.x is a descendent of http://openopc.sourceforge.net
with modifications for Python 3 and distutils.


About OpenOPC
-------------------
OpenOPC for Python is a free, open source OPC (OLE for Process Control)
toolkit designed for use with the popular Python programming language.


Software Developers
-------------------

If you elected to install the OpenOPC Development library during the
installation process, then you'll need to also download and install
the following packages in order to develop your own Python programs
which use the OpenOPC library:

1. Python 3.4+
   http://www.python.org/download/

2. Python for Windows Extensions (pywin32)
   http://sourceforge.net/projects/pywin32/

3. Pyro4
   https://github.com/irmen/Pyro4

Of course, Python is necessary on all platforms.  However the other
packages may be optional depending on your configuration:

1. Win32 platform, using the OpenOPC Gateway Service

Pywin32:  optional
Pyro4:    required

2. Win32 platform, talking to OPC Servers directly using COM/DCOM

Pywin32:  required
Pyro4:    optional

3. Non-Windows platform (use of Gateway Service is mandatory)

Pywin32:  not applicable
Pyro4:    required

In order to get the most from the OpenOPC package, Windows developers
are encouraged to install both Pywin32 and Pyro.  Using Pyro to talk to
the Gateway Service provides a quick and easy method for bypassing the
DCOM security nightmares which are all too common when using OPC.


Documentation
-------------

A PDF manual for OpenOPC is included in this installation inside the
"doc" folder.   Users are encouraged to also look at the OpenOPC web
site for additional usage examples that may not be contained in the
manual.

EXAMPLE: Minimal working program

    import OpenOPC
    opc = OpenOPC.client()
    opc.connect('Matrikon.OPC.Simulation')
    print(opc['Square Waves.Real8'])
    opc.close()


OpenOPC Command-line Client
---------------------------

OpenOPC includes the only publically available command-line OPC client.
Unlike graphical clients, it can be easily used in scripts or batch files.
And because of its piping capability (i.e. chaining commands together),
it is far more powerful than other OPC clients.

1. Get a listing of the available OPC servers on your computer by
going to the command prompt and entering:

    opc -q

2. Set your prefered OPC server as the default by setting the system
wide enviornment variable OPC_SERVER.  (On Windows you can do this
by going to Control Panel > System > Advanced > Environment Variables)

    OPC_SERVER=Matrikon.OPC.Simulation

3. Display OPC server information via the Win32 COM connection:

    opc -i

4. Test to see if the OpenOPC Gateway Service is functioning by
entering:

    opc -m open -i

5. Test some of the other commands available using the OPC Command
Line Client.  To get started, try entering the opc command without
any arguments in order to see the help page:

    opc

To read an item from your OPC server, just include the item name as
one of your arguments.  For example, if you're using Matrikon's
Simulation server you could do:

    opc Random.Int4

To read items from a specific OPC server you have installed,
include the -s switch followed by the OPC server name.  For
example:

    opc -s Matrikon.OPC.Simulation Random.Int4

To list available items:

    C:\> opc -f Random.*Int*
    Random.Int1
    Random.Int2
    Random.Int4
    Random.UInt1
    Random.UInt2
    Random.UInt4

To read values of items every 60 seconds, logging the results to a file
until stopped by Ctrl-C...:

    C:\> opc Random.Int4 Random.Real8 -L 60 >data.log

Command usage summary:

    C:\> opc 
    OpenOPC Command Line Client 1.1.6
    Copyright (c) 2007-2008 Barry Barnreiter (barry_b@users.sourceforge.net)
    
    Usage:  opc [OPTIONS] [ACTION] [ITEM|PATH...]
    
    Actions:
      -r, --read                 Read ITEM values (default action)
      -w, --write                Write values to ITEMs (use ITEM=VALUE)
      -p, --properties           View properties of ITEMs
      -l, --list                 List items at specified PATHs (tree browser)
      -f, --flat                 List all ITEM names (flat browser)
      -i, --info                 Display OPC server information
      -q, --servers              Query list of available OPC servers
      -S, --sessions             List sessions in OpenOPC Gateway Service
    
    Options:
      -m MODE, --mode=MODE       Protocol MODE (dcom, open) (default: OPC_MODE)
      -C CLASS,--class=CLASS     OPC Automation CLASS (default: OPC_CLASS)
      -n NAME, --name=NAME       Set OPC Client NAME (default: OPC_CLIENT)
      -h HOST, --host=HOST       DCOM OPC HOST (default: OPC_HOST)
      -s SERV, --server=SERVER   DCOM OPC SERVER (default: OPC_SERVER)
      -H HOST, --gate-host=HOST  OpenOPC Gateway HOST (default: OPC_GATE_HOST)
      -P PORT, --gate-port=PORT  OpenOPC Gateway PORT (default: OPC_GATE_PORT)
    
      -F FUNC, --function=FUNC   Read FUNCTION to use (sync, async)
      -c SRC,  --source=SOURCE   Set data SOURCE for reads (cache, device, hybrid)
      -g SIZE, --size=SIZE       Group tags into SIZE items per transaction
      -z MSEC, --pause=MSEC      Sleep MSEC milliseconds between transactions
      -u MSEC, --update=MSEC     Set update rate for group to MSEC milliseconds
      -t MSEC, --timeout=MSEC    Set read timeout to MSEC mulliseconds
    
      -o FMT,  --output=FORMAT   Output FORMAT (table, values, pairs, csv, html)
      -L SEC,  --repeat=SEC      Loop ACTION every SEC seconds until stopped
      -y ID,   --id=ID,...       Retrieve only specific Property IDs
      -a STR,  --append=STR,...  Append STRINGS to each input item name
      -x N     --rotate=N        Rotate output orientation in groups of N values
      -v,      --verbose         Verbose mode showing all OPC function calls
      -e,      --errors          Include descriptive error message strings
      -R,      --recursive       List items recursively when browsing tree
      -,       --pipe            Pipe item/value list from standard input

If you experience any unexpected errors, please check the FAQ on
http://openopc.sourceforge.net for additional help.

If after reading through the FAQ you still require additional help,
then the author of this package would be happy to assist you via
e-mail.  Please see the project website for current contact
information.


Technical Support
-----------------

If you have any questions, bug reports, or suggestions for improvements
please feel free to contact the author at:

barry_b@users.sourceforge.net

While I cannot always guarantee a quick response, I eventually respond
to all e-mails and will do my best to slove any issues which are discovered.

Thanks for using OpenOPC for Python!

Credits
-------
Copyright (c) 2008-2012 by Barry Barnreiter (barry_b@users.sourceforge.net)
Copyright (c) 2014 by Anton D. Kachalov (mouse@yandex.ru)
Copyright (c) 2017 by Michal Kwiatkowski (michal@trivas.pl)
Copyright (c) 2022 Yue BaoBao (yqbaowo@foxmail.com)

http://openopc.sourceforge.net/
https://github.com/ya-mouse/openopc
https://github.com/sightmachine/OpenOPC
https://github.com/YQBaobao/openopc
