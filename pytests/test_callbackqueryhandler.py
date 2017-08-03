#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import pytest

from telegram import Update, CallbackQuery, Bot
from telegram.ext import CallbackQueryHandler


@pytest.fixture
def callback_query(bot):
    return Update(0, callback_query=CallbackQuery(2, None, None, data="test data"))


class TestCallbackQueryHandler:
    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def cqh_test1(self, bot, update):
        test_bot = isinstance(bot, Bot)
        test_update = isinstance(update, Update)
        self.test_flag = test_bot and test_update

    def cqh_test2(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) or (chat_data is not None)

    def cqh_test3(self, bot, update, user_data=None, chat_data=None):
        self.test_flag = (user_data is not None) and (chat_data is not None)

    def cqh_test4(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) or (update_queue is not None)

    def cqh_test5(self, bot, update, job_queue=None, update_queue=None):
        self.test_flag = (job_queue is not None) and (update_queue is not None)

    def cqh_test6(self, bot, update, groups=None, groupdict=None):
        if groups is not None:
            self.test_flag = groups == ('t', ' data')
        if groupdict is not None:
            self.test_flag = groupdict == {'begin': 't', 'end': ' data'}

    def test_basic(self, dp, callback_query):
        handler = CallbackQueryHandler(self.cqh_test1)
        dp.add_handler(handler)

        assert handler.check_update(callback_query)

        dp.process_update(callback_query)
        assert self.test_flag

    def test_with_pattern(self, callback_query):
        handler = CallbackQueryHandler(self.cqh_test1, pattern='.*est.*')

        assert handler.check_update(callback_query)

        callback_query.callback_query.data = "nothing here"
        assert not handler.check_update(callback_query)

    def test_with_passing_group_dict(self, dp, callback_query):
        handler = CallbackQueryHandler(self.cqh_test6, pattern='(?P<begin>.*)est(?P<end>.*)',
                                       pass_groups=True)
        dp.add_handler(handler)

        dp.process_update(callback_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CallbackQueryHandler(self.cqh_test6, pattern='(?P<begin>.*)est(?P<end>.*)',
                                       pass_groupdict=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(callback_query)
        assert self.test_flag

    def test_pass_user_or_chat_data(self, dp, callback_query):
        handler = CallbackQueryHandler(self.cqh_test2, pass_user_data=True)
        dp.add_handler(handler)

        dp.process_update(callback_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CallbackQueryHandler(self.cqh_test2, pass_chat_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(callback_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CallbackQueryHandler(self.cqh_test3, pass_chat_data=True, pass_user_data=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(callback_query)
        assert self.test_flag

    def test_pass_job_or_update_queue(self, dp, callback_query):
        handler = CallbackQueryHandler(self.cqh_test4, pass_job_queue=True)
        dp.add_handler(handler)

        dp.process_update(callback_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CallbackQueryHandler(self.cqh_test4, pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(callback_query)
        assert self.test_flag

        dp.remove_handler(handler)
        handler = CallbackQueryHandler(self.cqh_test5, pass_job_queue=True, pass_update_queue=True)
        dp.add_handler(handler)

        self.test_flag = False
        dp.process_update(callback_query)
        assert self.test_flag