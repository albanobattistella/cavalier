# preferences_window.py
#
# Copyright 2022 Fyodor Sobolev
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written
# authorization.
#
# SPDX-License-Identifier: MIT

from gi.repository import Adw, Gtk, GObject, Gdk
from cavalier.settings import CavalierSettings


class CavalierPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'CavalierPreferencesWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_modal(False)
        self.settings = CavalierSettings.new(self.on_settings_changed)

        self.set_default_size(572, 518)
        self.create_cavalier_page()
        self.create_cava_page()
        self.create_colors_page()

    def create_cavalier_page(self):
        self.cavalier_page = Adw.PreferencesPage.new()
        self.cavalier_page.set_title('Cavalier')
        self.cavalier_page.set_icon_name('image-x-generic-symbolic')
        self.add(self.cavalier_page)

        self.cavalier_mode_group = Adw.PreferencesGroup.new()
        self.cavalier_mode_group.set_title(_('Drawing Mode'))
        self.cavalier_page.add(self.cavalier_mode_group)

        self.wave_row = Adw.ActionRow.new()
        self.wave_row.set_title(_('Wave'))
        self.wave_check_btn = Gtk.CheckButton.new()
        self.wave_row.add_prefix(self.wave_check_btn)
        self.wave_row.set_activatable_widget(self.wave_check_btn)
        self.cavalier_mode_group.add(self.wave_row)

        self.levels_row = Adw.ActionRow.new()
        self.levels_row.set_title(_('Levels'))
        self.levels_check_btn = Gtk.CheckButton.new()
        self.levels_check_btn.set_group(self.wave_check_btn)
        self.levels_row.add_prefix(self.levels_check_btn)
        self.levels_row.set_activatable_widget(self.levels_check_btn)
        self.cavalier_mode_group.add(self.levels_row)

        self.bars_row = Adw.ActionRow.new()
        self.bars_row.set_title(_('Bars'))
        self.bars_check_btn = Gtk.CheckButton.new()
        self.bars_check_btn.set_group(self.wave_check_btn)
        self.bars_row.add_prefix(self.bars_check_btn)
        self.bars_row.set_activatable_widget(self.bars_check_btn)
        self.cavalier_mode_group.add(self.bars_row)

        (self.wave_row, self.levels_row, self.bars_row)[ \
            ('wave', 'levels', 'bars').index(self.settings.get('mode')) \
            ].activate()
        self.wave_check_btn.connect('toggled', self.on_save, 'mode', 'wave')
        self.levels_check_btn.connect('toggled', self.on_save, 'mode', 'levels')
        self.bars_check_btn.connect('toggled', self.on_save, 'mode', 'bars')

        self.cavalier_group = Adw.PreferencesGroup.new()
        self.cavalier_page.add(self.cavalier_group)

        self.pref_margin = Adw.ActionRow.new()
        self.pref_margin.set_title(_('Drawing area margin'))
        self.pref_margin.set_subtitle( \
            _('Size of gaps around drawing area (in pixels).'))
        self.pref_margin_scale = Gtk.Scale.new_with_range( \
            Gtk.Orientation.HORIZONTAL, 0.0, 40.0, 1.0)
        self.pref_margin_scale.set_size_request(180, -1)
        self.pref_margin_scale.set_draw_value(True)
        self.pref_margin_scale.set_value_pos(Gtk.PositionType.LEFT)
        self.pref_margin_scale.set_value(self.settings.get('margin'))
        self.pref_margin_scale.connect('value-changed', self.on_save, \
            'margin', self.pref_margin_scale.get_value)
        self.pref_margin.add_suffix(self.pref_margin_scale)
        self.cavalier_group.add(self.pref_margin)

        self.pref_offset = Adw.ActionRow.new()
        self.pref_offset.set_title(_('Offset between items'))
        self.pref_offset.set_subtitle( \
            _('The size of spaces between elements in "levels" and "bars" modes (in percent).'))
        self.pref_offset_scale = Gtk.Scale.new_with_range( \
            Gtk.Orientation.HORIZONTAL, 0.0, 20.0, 1.0)
        self.pref_offset_scale.set_size_request(180, -1)
        self.pref_offset_scale.set_draw_value(True)
        self.pref_offset_scale.set_value_pos(Gtk.PositionType.LEFT)
        self.pref_offset_scale.set_value(self.settings.get('items-offset'))
        self.pref_offset_scale.connect('value-changed', self.on_save, \
            'items-offset', self.pref_offset_scale.get_value)
        self.pref_offset.add_suffix(self.pref_offset_scale)
        self.cavalier_group.add(self.pref_offset)

        self.pref_sharp_corners = Adw.ActionRow.new()
        self.pref_sharp_corners.set_title(_('Sharp corners'))
        self.pref_sharp_corners.set_subtitle( \
            _('Whether the main window corners should be sharp.'))
        self.pref_sharp_corners_switch = Gtk.Switch.new()
        self.pref_sharp_corners_switch.set_valign(Gtk.Align.CENTER)
        self.pref_sharp_corners_switch.set_active( \
            self.settings.get('sharp-corners'))
        # `state-set` signal returns additional parameter that we don't need,
        # that's why lambda is used. Also GtkSwitch's state is changed after
        # signal, so we have to pass the opposite of it
        self.pref_sharp_corners_switch.connect('state-set', \
            lambda *args : self.on_save(self.pref_sharp_corners_switch, \
                'sharp-corners', not self.pref_sharp_corners_switch.get_state()))
        self.pref_sharp_corners.add_suffix(self.pref_sharp_corners_switch)
        self.pref_sharp_corners.set_activatable_widget( \
            self.pref_sharp_corners_switch)
        self.cavalier_group.add(self.pref_sharp_corners)

    def create_cava_page(self):
        self.cava_page = Adw.PreferencesPage.new()
        self.cava_page.set_title('CAVA')
        self.cava_page.set_icon_name('utilities-terminal-symbolic')
        self.add(self.cava_page)

        self.cava_group = Adw.PreferencesGroup.new()
        self.cava_page.add(self.cava_group)

        self.bars_row = Adw.ActionRow.new()
        self.bars_row.set_title(_('Bars'))
        self.cava_group.add(self.bars_row)
        self.bars_scale = Gtk.Scale.new_with_range( \
            Gtk.Orientation.HORIZONTAL, 6.0, 50.0, 2.0)
        self.bars_scale.set_size_request(180, -1)
        self.bars_scale.set_draw_value(True)
        self.bars_scale.set_value_pos(Gtk.PositionType.LEFT)
        self.bars_scale.set_value(self.settings.get('bars'))
        self.bars_scale.set_increments(2.0, 2.0)
        self.bars_scale.connect('value-changed', self.on_bars_changed)
        self.bars_row.add_suffix(self.bars_scale)

        self.autosens_row = Adw.ActionRow.new()
        self.autosens_row.set_title(_('Automatic sensitivity'))
        self.autosens_row.set_subtitle( \
            _('Attempt to decrease sensitivity if the bars peak.'))
        self.autosens_switch = Gtk.Switch.new()
        self.autosens_switch.set_valign(Gtk.Align.CENTER)
        self.autosens_switch.set_active(self.settings.get('autosens'))
        # `state-set` signal returns additional parameter that we don't need,
        # that's why lambda is used. Also GtkSwitch's state is changed after
        # signal, so we have to pass the opposite of it
        self.autosens_switch.connect('state-set', \
            lambda *args : self.on_save(self.autosens_switch, \
                'autosens', not self.autosens_switch.get_state()))
        self.autosens_row.add_suffix(self.autosens_switch)
        self.autosens_row.set_activatable_widget(self.autosens_switch)
        self.cava_group.add(self.autosens_row)

        self.sensitivity_row = Adw.ActionRow.new()
        self.sensitivity_row.set_title(_('Sensitivity'))
        self.sensitivity_row.set_subtitle( \
            _('Manual sensitivity. If automatic sensitivity is enabled, this will only be the initial value.'))
        self.cava_group.add(self.sensitivity_row)
        self.sensitivity_scale = Gtk.Scale.new_with_range( \
            Gtk.Orientation.HORIZONTAL, 10.0, 250.0, 10.0)
        self.sensitivity_scale.set_size_request(150, -1)
        self.sensitivity_scale.set_draw_value(False)
        self.sensitivity_scale.set_value(self.settings.get('sensitivity'))
        self.sensitivity_scale.connect('value-changed', self.on_save, \
            'sensitivity', self.sensitivity_scale.get_value)
        self.sensitivity_row.add_suffix(self.sensitivity_scale)

        self.channels_row = Adw.ActionRow.new()
        self.channels_row.set_title(_('Channels'))
        self.cava_group.add(self.channels_row)
        self.channels_buttons_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.channels_buttons_box.add_css_class('linked')
        self.channels_buttons_box.set_valign(Gtk.Align.CENTER)
        self.channels_row.add_suffix(self.channels_buttons_box)
        self.btn_mono = Gtk.ToggleButton.new_with_label(_('Mono'))
        self.channels_buttons_box.append(self.btn_mono)
        self.btn_stereo = Gtk.ToggleButton.new_with_label(_('Stereo'))
        self.channels_buttons_box.append(self.btn_stereo)
        if self.settings.get('channels') == 'mono':
            self.btn_mono.set_active(True)
        else:
            self.btn_stereo.set_active(True)
        self.btn_mono.bind_property('active', self.btn_stereo, 'active', \
            (GObject.BindingFlags.BIDIRECTIONAL | \
             GObject.BindingFlags.SYNC_CREATE | \
             GObject.BindingFlags.INVERT_BOOLEAN))
        self.btn_mono.connect('toggled', self.on_channels_changed)
        self.btn_stereo.connect('toggled', self.on_channels_changed)

        self.smoothing_row = Adw.ComboRow.new()
        self.smoothing_row.set_title(_('Smoothing'));
        self.cava_group.add(self.smoothing_row);
        self.smoothing_row.set_model(Gtk.StringList.new([_('Off'), _('Monstercat')]))
        self.smoothing_row.set_selected( \
            ['off', 'monstercat'].index(self.settings.get('smoothing')))
        self.smoothing_row.connect('notify::selected-item', \
            lambda *args: self.settings.set('smoothing', \
            ['off', 'monstercat'][self.smoothing_row.get_selected()]))

        self.nr_row = Adw.ActionRow.new()
        self.nr_row.set_title(_('Noise Reduction'))
        self.nr_row.set_subtitle(_('0 - noisy, 1 - smooth'))
        self.cava_group.add(self.nr_row)
        self.nr_scale = Gtk.Scale.new_with_range( \
            Gtk.Orientation.HORIZONTAL, 0.0, 1.0, 0.01)
        self.nr_scale.add_mark(0.77, Gtk.PositionType.BOTTOM, None)
        self.nr_scale.set_size_request(190, -1)
        self.nr_scale.set_draw_value(True)
        self.nr_scale.set_value_pos(Gtk.PositionType.LEFT)
        self.nr_scale.get_first_child().set_margin_bottom(12)
        self.nr_scale.set_value(self.settings.get('noise-reduction'))
        self.nr_scale.connect('value-changed', self.on_save, \
            'noise-reduction', self.nr_scale.get_value)
        self.nr_row.add_suffix(self.nr_scale)

    def create_colors_page(self):
        self.colors_page = Adw.PreferencesPage.new()
        self.colors_page.set_title(_('Colors'))
        self.colors_page.set_icon_name('applications-graphics-symbolic')
        self.add(self.colors_page)

        self.style_group = Adw.PreferencesGroup.new()
        self.colors_page.add(self.style_group)

        self.style_row = Adw.ActionRow.new()
        self.style_row.set_title(_('Widgets style'))
        self.style_row.set_subtitle(_('Style used by Adwaita widgets.'))
        self.style_buttons_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.style_buttons_box.add_css_class('linked')
        self.style_buttons_box.set_valign(Gtk.Align.CENTER)
        self.style_row.add_suffix(self.style_buttons_box)
        self.btn_light = Gtk.ToggleButton.new_with_label(_('Light'))
        self.style_buttons_box.append(self.btn_light)
        self.btn_dark = Gtk.ToggleButton.new_with_label(_('Dark'))
        self.style_buttons_box.append(self.btn_dark)
        if self.settings.get('widgets-style') == 'light':
            self.btn_light.set_active(True)
        else:
            self.btn_dark.set_active(True)
        self.btn_dark.bind_property('active', self.btn_light, 'active', \
            (GObject.BindingFlags.BIDIRECTIONAL | \
             GObject.BindingFlags.SYNC_CREATE | \
             GObject.BindingFlags.INVERT_BOOLEAN))
        self.btn_light.connect('toggled', self.apply_style)
        self.btn_dark.connect('toggled', self.apply_style)
        self.style_group.add(self.style_row)

        self.fg_colors = self.settings.get('fg-colors')
        self.bg_colors = self.settings.get('bg-colors')

        self.colors_group = Adw.PreferencesGroup.new()
        self.colors_group.set_title(_('Colors'))
        self.colors_page.add(self.colors_group)

        self.colors_grid = Gtk.Grid.new()
        self.colors_grid.add_css_class('card')
        self.colors_grid.set_column_homogeneous(True)
        self.colors_group.add(self.colors_grid)
        self.fg_lbl = Gtk.Label.new(_('<b>Foreground</b>'))
        self.fg_lbl.set_use_markup(True)
        self.fg_lbl.set_margin_top(12)
        self.fg_lbl.set_margin_bottom(12)
        self.colors_grid.attach(self.fg_lbl, 0, 0, 1, 1)
        self.bg_lbl = Gtk.Label.new(_('<b>Background</b>'))
        self.bg_lbl.set_use_markup(True)
        self.bg_lbl.set_margin_top(12)
        self.bg_lbl.set_margin_bottom(12)
        self.colors_grid.attach(self.bg_lbl, 1, 0, 1, 1)
        self.fg_color_btns = []
        self.bg_color_btns = []
        self.fill_colors_grid()

    def fill_colors_grid(self):
        counter = 0
        for fg_color in self.fg_colors:
            box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
            box.set_halign(Gtk.Align.CENTER)
            box.set_margin_top(6)
            box.set_margin_bottom(6)
            color = Gdk.RGBA()
            Gdk.RGBA.parse(color, 'rgba(%d, %d, %d, %f)' % fg_color)
            color_btn = Gtk.ColorButton.new_with_rgba(color)
            color_btn.set_use_alpha(True)
            color_btn.set_size_request(98, -1)
            color_btn.connect('color-set', self.color_changed, 0, counter)
            box.append(color_btn)
            rm_btn = Gtk.Button.new_from_icon_name('edit-delete-symbolic')
            rm_btn.add_css_class('circular')
            if counter == 0:
                rm_btn.set_sensitive(False)
            rm_btn.connect('clicked', self.remove_color, 0, counter)
            box.append(rm_btn)
            self.colors_grid.attach(box, 0, counter + 1, 1, 1)
            counter += 1
        if counter < 10:
            self.fg_add_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 4)
            self.fg_add_box.set_halign(Gtk.Align.CENTER)
            self.fg_add_box.set_valign(Gtk.Align.CENTER)
            self.fg_add_box.set_margin_bottom(6)
            self.fg_add_box.append(Gtk.Label.new(_('Add')))
            color = Gdk.RGBA()
            Gdk.RGBA.parse(color, '#000f')
            self.fg_add_colorbtn = Gtk.ColorButton.new_with_rgba(color)
            self.fg_add_colorbtn.set_use_alpha(True)
            self.fg_add_box.append(self.fg_add_colorbtn)
            self.fg_add_btn = Gtk.Button.new_from_icon_name('list-add-symbolic')
            self.fg_add_btn.add_css_class('circular')
            self.fg_add_btn.connect('clicked', self.add_color, 0)
            self.fg_add_box.append(self.fg_add_btn)
            self.colors_grid.attach(self.fg_add_box, 0, counter + 1, 1, 1)
        counter = 0
        for bg_color in self.bg_colors:
            box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
            box.set_halign(Gtk.Align.CENTER)
            box.set_margin_top(6)
            box.set_margin_bottom(6)
            color = Gdk.RGBA()
            Gdk.RGBA.parse(color, 'rgba(%d, %d, %d, %f)' % bg_color)
            color_btn = Gtk.ColorButton.new_with_rgba(color)
            color_btn.set_use_alpha(True)
            color_btn.set_size_request(98, -1)
            color_btn.connect('color-set', self.color_changed, 1, counter)
            box.append(color_btn)
            rm_btn = Gtk.Button.new_from_icon_name('edit-delete-symbolic')
            rm_btn.add_css_class('circular')
            rm_btn.connect('clicked', self.remove_color, 1, counter)
            box.append(rm_btn)
            self.colors_grid.attach(box, 1, counter + 1, 1, 1)
            counter += 1
        if counter < 10:
            self.bg_add_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 4)
            self.bg_add_box.set_halign(Gtk.Align.CENTER)
            self.bg_add_box.set_valign(Gtk.Align.CENTER)
            self.bg_add_box.set_margin_bottom(6)
            self.bg_add_box.append(Gtk.Label.new(_('Add')))
            color = Gdk.RGBA()
            Gdk.RGBA.parse(color, '#000f')
            self.bg_add_colorbtn = Gtk.ColorButton.new_with_rgba(color)
            self.bg_add_colorbtn.set_use_alpha(True)
            self.bg_add_box.append(self.bg_add_colorbtn)
            self.bg_add_btn = Gtk.Button.new_from_icon_name('list-add-symbolic')
            self.bg_add_btn.add_css_class('circular')
            self.bg_add_btn.connect('clicked', self.add_color, 1)
            self.bg_add_box.append(self.bg_add_btn)
            self.colors_grid.attach(self.bg_add_box, 1, counter + 1, 1, 1)

    def clear_colors_grid(self):
        while True:
            if (self.colors_grid.get_child_at(0, 1) != None) or \
                    (self.colors_grid.get_child_at(1, 1) != None):
                self.colors_grid.remove_row(1)
            else:
                break

    def add_color(self, obj, color_type): # color_type 0 for fg, 1 for bg
        if color_type == 0:
            color = self.fg_add_colorbtn.get_rgba()
            self.fg_colors.append((round(color.red * 255), \
                round(color.green * 255), round(color.blue * 255), color.alpha))
            self.settings.set('fg-colors', self.fg_colors)
        else:
            color = self.bg_add_colorbtn.get_rgba()
            self.bg_colors.append((round(color.red * 255), \
                round(color.green * 255), round(color.blue * 255), color.alpha))
            self.settings.set('bg-colors', self.bg_colors)

    def remove_color(self, obj, color_type, index):
        if color_type == 0:
            self.fg_colors.pop(index)
            self.settings.set('fg-colors', self.fg_colors)
        else:
            self.bg_colors.pop(index)
            self.settings.set('bg-colors', self.bg_colors)

    def color_changed(self, obj, color_type, index):
        if color_type == 0:
            self.fg_colors.pop(index)
            color = obj.get_rgba()
            self.fg_colors.insert(index, (round(color.red * 255), \
                round(color.green * 255), round(color.blue * 255), color.alpha))
            self.settings.set('fg-colors', self.fg_colors)
        else:
            self.bg_colors.pop(index)
            color = obj.get_rgba()
            self.bg_colors.insert(index, (round(color.red * 255), \
                round(color.green * 255), round(color.blue * 255), color.alpha))
            self.settings.set('bg-colors', self.bg_colors)

    def apply_style(self, obj):
        if self.btn_light.get_active():
            self.settings.set('widgets-style', 'light')
        else:
            self.settings.set('widgets-style', 'dark')

    def on_bars_changed(self, obj):
        value = self.bars_scale.get_value()
        if value % 2 != 0:
            value -= 1
            self.bars_scale.set_value(value)
        self.on_save(obj, 'bars', value)

    def on_channels_changed(self, obj):
        if self.btn_mono.get_active():
            self.settings.set('channels', 'mono')
        else:
            self.settings.set('channels', 'stereo')

    def on_save(self, obj, key, value):
        if callable(value):
            value = value()
        if type(value) is float and type(self.settings.get(key)) is int:
            value = round(value)
        self.settings.set(key, value)

    def on_settings_changed(self):
        try: # settings are initialized before colors_grid
            self.clear_colors_grid()
            self.fill_colors_grid()
        except:
            pass
