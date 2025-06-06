import os
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class Guide:
    def __init__(self, args, auth):
        self.args = args
        self.auth = auth

    def save(self):
        channels = self.get_channels()
        playlist = self.get_playlist(channels)
        self.save_playlist(playlist)
        self.save_guide_info(channels)

    def get_channels(self):
        # 有个tempKey 不知道是怎么算的 所以先不传 暂时能获取到数据
        params = {
            'UserID': self.args.user,
            'Lang': '1',
            'SupportHD': '1',
            'stbid': self.auth.stbid,
            'UserToken': self.auth.token,
            'conntype': '',
        }
        for i in range(5):
            try:
                response = self.auth.session.post(self.auth.base_url + '/EPG/jsp/getchannellistHWCTC.jsp', params=params)
                soup = BeautifulSoup(response.text, 'html.parser')
                scripts = soup.find_all('script', string=re.compile('ChannelID="[^"]+"'))
                print(f'Found {len(scripts)} channels')
                channels = []
                filtered_channels = 0
                for script in scripts:
                    match = re.search(r'Authentication.CTCSetConfig\(\'Channel\',\'(.+?)\'\)', script.string, re.MULTILINE)
                    channel_params = match.group(1)
                    channel = {}
                    for channel_param in channel_params.split('",'):
                        key, value = channel_param.split('="')
                        channel[key] = value
                    if self.match_channel_filters(channel):
                        filtered_channels += 1
                    else:
                        channels.append(channel)
                print(f'Filtered {filtered_channels} channels')
                removed_sd_candidate_channels = self.remove_sd_candidate_channels(channels)
                print(f'Removed {removed_sd_candidate_channels} SD candidate channels')
                return channels
            except Exception:
                time.sleep(5)

    def match_channel_filters(self, channel):
        name = channel['ChannelName']
        if "测试" in name:
            return True
        if "导视" in name:
            return True
        if "直播" in name:
            return True
        if "购" in name:
            return True
        for channel_filter in self.args.filter:
            match = re.search(channel_filter, name)
            if match:
                return True
        return False

    def remove_sd_candidate_channels(self, channels):
        if self.args.all_channel:
            return 0
        channels_count = len(channels)
        channels[:] = [channel for channel in channels if not Guide.is_sd_candidate_channel(channel, channels)]
        new_channels_count = len(channels)
        return channels_count - new_channels_count

    @staticmethod
    def is_sd_candidate_channel(channel, channels):
        for c in channels:
            if c['ChannelName'] == channel['ChannelName'] + '高清':
                return True
        return False

    def get_playlist(self, channels):
        channel_infos = {}
        for i in range(3):
            response = self.auth.session.get(self.auth.base_url + '/EPG/jsp/gdhdpublic/Ver.3/common/data.jsp?Action=channelListAll')
            data = json.parse(response.text)
            lst = data['result']
            for info in lst:
                channel_infos[info['channelID']] = info
            pass
        content = '#EXTM3U\n'
        for channel in channels:
            channel_id = channel['ChannelID']
            item = f"#EXTINF:-1 tvg-id=\"{channel_id}\","
            if channel_id in channel_infos:
                info = channel_infos[channel_id]
                item += f"tvg-logo=\"{info['pic']}\","
            if channel['TimeShift'] == "1":
                item += ('catchup="default",catchup-source="%s&playseek=${(b)yyyyMMddHHmmss}-${(e)yyyyMMddHHmmss}",'
                         % channel["TimeShiftURL"]
                         )
            item += f"{channel['ChannelName']}\n"
            full_url = channel['ChannelURL']
            if self.args.igmpProxy != "" and "igmp://" in full_url:
                match = re.search(r'igmp://([\d\.\:]+)', full_url)
                if match:
                    channel_url = self.args.igmpProxy + match.group(1)
            if channel_url is None:
                match = re.search(r'rtsp://[^\|]+', full_url)
                if match:
                    channel_url = match.group(0)
            if channel_url:
                content += item
                content += f"{channel_url}\n"
            else:
                print(f'channel :{channel_id} {channel["ChannelName"]} can not find andy url')
        return content

    def save_playlist(self, playlist):
        path = os.path.abspath(self.args.output+"/iptv.m3u8")
        Guide.save_file(path, playlist)
        print(f'Playlist saved to {path}')

    @staticmethod
    def save_file(file, content):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            f.write(content)
            f.close()

    def save_guide_info(self, channels):
        path = os.path.abspath(self.args.output+"/epg.xml")
        today = datetime.now()
        root = ET.Element('tv', {
            'generator-info-name': '浙江电信'
        })
        for channel in channels:
            channel_id = channel['ChannelID']
            params = {
                "Action": "channelProgramList",
                'channelId': channel_id
            }
            channel_name = channel["ChannelName"]
            channel_el = ET.SubElement(root, 'channel', {'id': f'{channel_id}'})
            display_name = ET.SubElement(channel_el, 'display-name')
            display_name.set('lang', 'zh')
            display_name.text = channel_name

            for i in range(9):
                if i == 8 and today.hour < 21:
                    # 21点之后才可以获取第二天数据
                    break
                if i < 7 and channel["TimeShift"] == "0":
                    # 不能时移的频道只有预告
                    continue
                params["date"] = (today - timedelta(days=7-i)).strftime('%Y%m%d')
                for j in range(3):
                    try:
                        response = self.auth.session.get(self.auth.base_url + '/EPG/jsp/gdhdpublic/Ver.3/common/data.jsp',
                                                         params=params)
                        data = json.parse(response.text)
                        result = data["result"]
                        if isinstance(result, list):
                            for item in data['result']:
                                day = item['day'].replace('-', '')
                                start_time = item['time'].replace(':', '')
                                stop_time = item['endtime'].replace(':', '')
                                start = f"{day}{start_time} +0800"
                                stop = f"{day}{stop_time} +0800"
                                programme = ET.SubElement(root, 'programme', {
                                    'start': start,
                                    'stop': stop,
                                    'channel': f'{channel_id}'
                                })
                                title = ET.SubElement(programme, 'title')
                                title.set('lang', 'zh')
                                title.text = item['name']
                        break
                    except Exception:
                        sleep(2)
        tree = ET.ElementTree(root)
        tree.write(path, encoding='utf-8', xml_declaration=True)






