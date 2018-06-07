from flask import url_for, render_template
from flask_restful import Resource
from common.entity.entities import Sector


class Home(Resource):
    def get(self):
        sectors_list = Sector.SECTORS
        refresh_url = url_for('refresh_active_nodes')
        reboot_bbb_url = url_for('reboot_bbb')
        switch_bbb_url = url_for('switch_bbb')
        return render_template('index.html', refresh_url=refresh_url, switch_bbb_url=switch_bbb_url,
                               reboot_bbb_url=reboot_bbb_url, sectors=sectors_list)
