---
title: XFCE4 and Eclipse IDE

summary: Why Eclipse looks ugly under XFCE4 and how to fix it.
---

*XFCE* is nice graphical environment, because has simple yet functional layout and 
does not consume CPU power too much. *Eclipse* is nice too. It has clear interface 
and plugins system with plenty of addons and useful keyboard shourtcuts.

Unfortunatelly *XFCE4* and *Eclipse* do not like each other. It becomes clear after 
looking at following image (note IDE's Toolbar):
[![Eclipse with GUI problems](/img/post/2022-10-27/eclipse-fail-small.png "Eclipse with GUI problems")](/img/post/2022-10-27/eclipse-fail.png)

Until recent workaround I used was to run *Eclipse* in GTK2 compatibility mode. 
It can be done by adding following lanes:
```
--launcher.GTK_version
2
```
to *eclipse.ini*. There is one problem with this solution: it does not work with modern 
releases of the IDE, because it dropped compatibility with GTK2. 

Because of the problem I had to try other desktop environments. Under *Cinnamon* 
*Eclipse* looks smoothly without any workarounds. Big suprprise was that *Cinnamon* 
uses GTK3, so the widget toolkit was not the case, so I went back to *XFCE* and started 
playing with varius options of the environment. Then it became apparent that *XFCE* 
appearance style was the case.


### Fix

The problem appears if You use *Greybird* appearance style. Fixing the style requires 
editing *gtk.css* file of the style. To do so, follow the steps:
1. locate built-in *Greyscale* theme in `/usr/share/themes/`
2. copy the theme into local direcoty `~/.local/share/themes/Greybird-Original`
3. copy the theme into local direcoty `~/.local/share/themes/Greybird`
4. open CSS file `~/.local/share/themes/Greybird/gtk-3.0/gtk.css`
5. change following text (around line 179):
```
notebook > header > tabs > arrow, button.titlebutton, button { min-height: 24px; min-width: 22px; padding: 1px 2px; border: 1px solid; border-radius: 3px; transition: all 200ms cubic-bezier(0.25, 0.46, 0.45, 0.94); color: #3c3c3c; outline-color: rgba(60, 60, 60, 0.3); border-top-color: shade(#cecece, 0.8); border-right-color: shade(#cecece, 0.72); border-left-color: shade(#cecece, 0.72); border-bottom-color: shade(#cecece, 0.7); background-image: linear-gradient(to bottom, shade(shade(#cecece, 1.02), 1.05), shade(shade(#cecece, 1.02), 0.97)); box-shadow: inset 0 1px rgba(255, 255, 255, 0.6); }
```
with
```
notebook > header > tabs > arrow, button.titlebutton, button { min-height: 24px; min-width: 16px; padding: 1px 2px; border: 1px solid; border-radius: 3px; transition: all 200ms cubic-bezier(0.25, 0.46, 0.45, 0.94); color: #3c3c3c; outline-color: rgba(60, 60, 60, 0.3); border-top-color: shade(#cecece, 0.8); border-right-color: shade(#cecece, 0.72); border-left-color: shade(#cecece, 0.72); border-bottom-color: shade(#cecece, 0.7); background-image: linear-gradient(to bottom, shade(shade(#cecece, 1.02), 1.05), shade(shade(#cecece, 1.02), 0.97)); box-shadow: inset 0 1px rgba(255, 255, 255, 0.6); }
```
6. replace following text (around line 552):
```
toolbar { background: #cecece linear-gradient(to bottom, #cecece, shade(#cecece, 0.88)); box-shadow: inset 0 1px rgba(255, 255, 255, 0.8); box-shadow: none; border-bottom: 1px solid #828282; padding: 4px 3px 3px 4px; }
```
with
```
toolbar { background: none; box-shadow: inset 0 1px rgba(255, 255, 255, 0.8); box-shadow: none; }
```
7. change style in *Settings->Appearance->Stype* to *Greybird*

Patched file can be found [*here*](/img/post/2022-10-27/gtk.css) (based on Xfce 4.14).

Note: some applications and system components depends on name of theme, so copying and editing *Greybird* in user local directory does not break them. One of those application is *Notes* and it's appearance on task bar. Creating *Greybird-Original* copy allows comparing with standard version.

After applying the fix *Eclipse* will look like:
[![Eclipse fixed](/img/post/2022-10-27/eclipse-ok-small.png "Eclipse fixed")](/img/post/2022-10-27/eclipse-ok.png)


## References

- [Installing new theme](https://wiki.xfce.org/howto/install_new_themes)
- [Eclipse: force GTK2](https://www.eclipse.org/forums/index.php/t/1071268/)
