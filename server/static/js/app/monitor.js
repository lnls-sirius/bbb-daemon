(function(){
    // @fixme: use npm to manage the .js files. Use templates instead of the hardcoded html (mustache could be a good idea)!
    /**
        This is a chart !
    */
    function NodeChart(canvasId, label, bgColor, borderColor){
        this.canvasId = canvasId;

        // Search dom
        this.canvas = document.getElementById(this.canvasId).getContext('2d');

        // Chart.js
        this.chartjs = new Chart(this.canvas, {
            responsive: true,
            type: 'bar',
            data: {
                datasets: [{
                    label: label,
                    borderWidth: 1,
                    backgroundColor: bgColor,
                    borderColor: borderColor
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }],
                    xAxes: [{
                        stacked: false,
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            min: 0,
                            autoSkip: false
                        }
                    }]
                }
            }
        });

        this.clearChart = function() {
            if (this.chartjs) {
                this.chartjs.data.datasets.forEach((dataset) => {
                    dataset.data = [];
                });
            }
        };

        this.setChartData = function (lbls, data) {
            if (this.chartjs) {
                this.chartjs.data.labels = lbls;
                this.chartjs.data.datasets.forEach((dataset) => {
                    dataset.data = data;
                });
            }
        };

        this.update = function (){
            this.chartjs.update();
        };
    };

    function BtnSwitch(){
        // Load from DOM
        this.btnSwitchDom = document.getElementById("btn_switch_bbb");

        // Update Status
        this.updateBtnStatus = function (){
            this.btnSwitchDom.innerHTML =
                "Switch <strong> <br>Configured:\t" + bbb_configured_selected['name'] + "\t\tIP:" + bbb_configured_selected['ip']
                + "<br>Not Configured:\t" + bbb_unconfigured_selected['name'] + "\t\tIP:" + bbb_unconfigured_selected['ip'] + "</strong>";

            this.btnSwitchDom.disabled = (bbb_unconfigured_selected['name'] === '' || bbb_configured_selected['name'] === '');
        };

        this.disable = function (){
            this.btnSwitchDom.disable = true;
            this.updateBtnStatus();
        };

        this.switchBBB = function() {
            if (bbb_configured_selected['name'] !== '' && bbb_unconfigured_selected['name'] !== '') {
                const objToSend = {
                    c_bbb: {
                        name: bbb_configured_selected['name'],
                        ip: bbb_configured_selected['ip'],
                        sector: active_sector_val,
                    },
                    u_bbb: {
                        name: bbb_unconfigured_selected['name'],
                        ip: bbb_unconfigured_selected['ip'],
                        sector: active_sector_val,
                    }
                };
                const json = JSON.stringify(objToSend);
                $.post('/bbb/',
                    {
                        action:'switch',
                        data: json
                    }, null, 'json'
                ).done(function (data) {
                    bbb_configured_selected['name'] = '';
                    bbb_configured_selected['ip'] = '';
    
                    bbb_unconfigured_selected['name'] = '';
                    bbb_unconfigured_selected['ip'] = '';
    
                    console.log('reset selection!' + data);
                    btnSwitch.updateBtnStatus();
                });
            }
        };

        // Add onclick
        this.btnSwitchDom.addEventListener('click', this.switchBBB);

    };

    function AppStates(){
        // Seach the Dom
        this.sectorSelect = document.getElementById('current_sector');
        this.confTBody = document.getElementById('confTBody');
        this.uconfTBody = document.getElementById('uconfTBody');
    

        this.getActiveSector = function(){
            return this.sectorSelect.value;
        }

        this.bbbConfiguredSelected  = {
            name: '',
            ip : ''
        };

        this.bbbUnconfiguredSelected = {
            name: '',
            ip : ''
        };

        this.resetConf = function(){
            this.bbbConfiguredSelected['name'] = '';
            this.bbbConfiguredSelected['ip'] = '';
        }

        this.resetUconf = function(){
            this.bbbUnconfiguredSelected['name'] = '';
            this.bbbUnconfiguredSelected['ip'] = '';
        }

        this.resetAll = function(){
            this.resetConf();
            this.resetUconf();
        };
    }

    // Initialization !
    const appStates = new AppStates();

    const chartC = new NodeChart('cChart', 'Configured Nodes','rgb(144, 238, 144)','rgb(50, 205, 50)');
    const chartU = new NodeChart('uChart', 'Not Configured Nodes','rgb( 238, 144, 144)','rgb(205,50, 50)');

    
    const btnSwitch = new BtnSwitch();
    // @todo: move to appStates obj !
    const bbb_configured_selected = {
        name: '',
        ip: ''
    };
    const bbb_unconfigured_selected = {
        name: '',
        ip: ''
    };

    var active_sector_val = null;

    /**
    * Removel all children
    */
    function removeChild(node) {
        if (node) {
            while (node.firstChild) {
                node.removeChild(node.firstChild);
            }
        }
    }

    /**
        Get a row from node !
    */
    function getRow(node, configured) {
        const tr = document.createElement('tr');
        // self.details = details
        // self.configTime = configTime
        // self.device = device
        const td_name = document.createElement('td');
        td_name.innerText = node['name'];

        const td_ip = document.createElement('td');
        td_ip.innerText = node['ipAddress'];

        const td_details = document.createElement('td');
        td_details.innerText = node['details'];

        const td_device = document.createElement('td');
        td_device.innerText = node['device'];

        const td_configTime = document.createElement('td');
        td_configTime.innerText = node['configTime'];

        const td_type_name = document.createElement('td');
        td_type_name.innerText = (node['type'])?(node['type']['name']):('Type not set !');

        const td_repo = document.createElement('td');
        td_repo.innerText = (node['type'])?(node['type']['repoUrl']):('Type not set !');

        const td_rc = document.createElement('td');
        td_rc.innerText = node['rcLocalPath'];

        const td_sector = document.createElement('td');
        td_sector.innerText = node['sector'];

        const td_pref = document.createElement('td');
        td_pref.innerText = node['pvPrefix'];

        const td_state = document.createElement('td');
        td_state.innerText = node['state_string'];

        const td_reboot = document.createElement('td');
        const btn_reboot = document.createElement('button');
        btn_reboot.setAttribute('type', 'butt1');
        btn_reboot.setAttribute('configured', configured);
        btn_reboot.addEventListener('click', rebootThis);
        btn_reboot.setAttribute('myName', node['name']);
        btn_reboot.setAttribute('myIp', node['ipAddress']);
        btn_reboot.setAttribute('class', 'btn btn-danger');
        btn_reboot.innerText = 'Reboot BBB';

        switch (node['state']) {
            case 0: // Disconnected
                td_state.innerText = 'Disconnected';
                btn_reboot.setAttribute('disabled', '');
                tr.setAttribute('class', 'bg-danger');
                break;
            case 1: // Misconfigured
                td_state.innerText = 'Misconfigured';
                btn_reboot.removeAttribute('disabled');
                tr.setAttribute('class', 'bg-danger');
                break;
            case 2: // Connected
                td_state.innerText = 'Connected';
                btn_reboot.removeAttribute('disabled');
                tr.setAttribute('class', ' bg-success');
                break;
            case 3: // Rebooting
                td_state.innerText = 'Rebooting';
                btn_reboot.setAttribute('disabled', '');
                tr.setAttribute('class', 'bg-warning');
                break;
            default:

        }

        td_reboot.appendChild(btn_reboot);

        tr.appendChild(td_name);
        tr.appendChild(td_ip);
        tr.appendChild(td_details);
        tr.appendChild(td_device);
        tr.appendChild(td_configTime);
        tr.appendChild(td_type_name);
        tr.appendChild(td_repo);
        tr.appendChild(td_rc);
        tr.appendChild(td_sector);
        tr.appendChild(td_pref);
        tr.appendChild(td_state);
        tr.appendChild(td_reboot);

        return tr;
    }

    function rebootThis(e) {
        const myIp = this.getAttribute("myIp");
        const configured = this.getAttribute("configured");
        $.post('/bbb/',{
                action:'reboot',
                ip: myIp,
                sector: active_sector_val,
                configured: configured}
        ).done(function (data) {
            console.log('Reboot' + data);
        });
    }

    function refresh_chart() {
        $.post(
            '/node/',{action: 's_c_u'}
        ).done(function (data, success) {
            if (success) {

                chartC.clearChart();
                chartU.clearChart();

                chartC.setChartData( data['lbls'], data['c_vals']);
                chartU.setChartData( data['lbls'], data['u_vals']);

                chartC.update();
                chartU.update();
            }
        });
    }

    function refresh_bbbs() {
        var current_sector_val = appStates.getActiveSector();

        if (active_sector_val !== current_sector_val) {
            active_sector_val = current_sector_val;

            bbb_configured_selected['name'] = '';
            bbb_configured_selected['ip'] = '';

            bbb_unconfigured_selected['name'] = '';
            bbb_unconfigured_selected['ip'] = '';

            btnSwitch.disable();
        }

        $.post('/node/',{
                'action':'conf_uconf',
                'sector': current_sector_val
            })
            .done(function (data, success) {
                if (success) {
                    try{
                        console.log(data);

                        let i;

                        const cNodes = data['configured_nodes'];
                        const uNodes = data['unconfigured_nodes'];
                        
                        removeChild(appStates.confTBody);
                        removeChild(appStates.uconfTBody);


                        for (i = 0; i < cNodes.length; i++) {
                            if(cNodes[i]){
                                const tr = getRow(cNodes[i], true);
                                tr.addEventListener('click', selectRowConf);
                                appStates.confTBody.appendChild(tr);
                            }
                        }

                        for (i = 0; i < uNodes.length; i++) {
                            if(uNodes[i]){
                                const tr = getRow(uNodes[i], false);
                                tr.addEventListener('click', selectRowUconf);
                                appStates.uconfTBody.appendChild(tr);
                            }
                        }
                    }catch(err){
                        console.log(err.message);
                        console.log((data['message']?data['message']:''));
                    }
                }
            });
    }

    function selectRowConf(e) {
        // First column is the status one ...
        const name = this.childNodes[0].innerText;
        const ip = this.childNodes[1].innerText;

        if (name === bbb_configured_selected['name']) {
            bbb_configured_selected['name'] = '';
            bbb_configured_selected['ip'] = '';

        } else {

            bbb_configured_selected['name'] = name;
            bbb_configured_selected['ip'] = ip;

        }
        btnSwitch.updateBtnStatus();
    }

    function selectRowUconf(e) {

        // First column is the status one ...
        const name = this.childNodes[0].innerText;
        const ip = this.childNodes[1].innerText;

        if (name === bbb_unconfigured_selected['name']) {

            bbb_unconfigured_selected['name'] = '';
            bbb_unconfigured_selected['ip'] = '';

        } else {

            bbb_unconfigured_selected['name'] = name;
            bbb_unconfigured_selected['ip'] = ip;
        }
        btnSwitch.updateBtnStatus();
    }

    refresh_bbbs();
    refresh_chart();

    setInterval(function () {
        refresh_bbbs()
    }, 2000);

    setInterval(function () {
        refresh_chart()
    }, 2000);

})()

