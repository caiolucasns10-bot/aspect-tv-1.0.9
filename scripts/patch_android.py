import re,glob
J='''package com.aspect.player;
import android.app.PictureInPictureParams;
import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.os.Build;
import android.os.Bundle;
import android.util.Rational;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
  boolean playing = false;
  WindowInsetsControllerCompat ctl;

  @Override public void onCreate(Bundle b) {
    super.onCreate(b);
    final Window w = getWindow();
    final int bg = Color.parseColor("#050505");
    WindowCompat.setDecorFitsSystemWindows(w, false);
    w.setStatusBarColor(bg);
    w.setNavigationBarColor(bg);
    w.setBackgroundDrawable(new ColorDrawable(bg));
    if (Build.VERSION.SDK_INT >= 28)
      w.getAttributes().layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
    ctl = WindowCompat.getInsetsController(w, w.getDecorView());
    ctl.setAppearanceLightStatusBars(false);
    ctl.setAppearanceLightNavigationBars(false);
    ctl.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
    final WebView wv = getBridge().getWebView();
    wv.setBackgroundColor(bg);
    ViewCompat.setOnApplyWindowInsetsListener(wv, (v, ins) -> {
      Insets s = ins.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.displayCutout());
      float d = getResources().getDisplayMetrics().density;
      js("var r=document.documentElement.style;r.setProperty('--safe-area-inset-top','" + (s.top / d) + "px');r.setProperty('--safe-area-inset-bottom','" + (s.bottom / d) + "px');r.setProperty('--safe-area-inset-left','" + (s.left / d) + "px');r.setProperty('--safe-area-inset-right','" + (s.right / d) + "px')");
      return WindowInsetsCompat.CONSUMED;
    });
    ViewCompat.requestApplyInsets(wv);
    wv.addJavascriptInterface(new Object() {
      @JavascriptInterface public void immersive(final boolean on) {
        runOnUiThread(() -> { if (on) ctl.hide(WindowInsetsCompat.Type.systemBars()); else ctl.show(WindowInsetsCompat.Type.systemBars()); });
      }
      @JavascriptInterface public void pip() { runOnUiThread(() -> enterPip()); }
      @JavascriptInterface public void setPlaying(boolean p) { playing = p; }
    }, "AspectNative");
  }

  void js(final String c) { runOnUiThread(() -> getBridge().getWebView().evaluateJavascript(c, null)); }

  void enterPip() {
    if (Build.VERSION.SDK_INT >= 26)
      try { enterPictureInPictureMode(new PictureInPictureParams.Builder().setAspectRatio(new Rational(16, 9)).build()); } catch (Exception e) {}
  }

  @Override public void onUserLeaveHint() { super.onUserLeaveHint(); if (playing) enterPip(); }

  @Override public void onPictureInPictureModeChanged(boolean in, Configuration c) {
    super.onPictureInPictureModeChanged(in, c);
    js("window.onPip&&onPip(" + in + ")");
  }
}
'''
p=glob.glob('android/app/src/main/java/**/MainActivity.java',recursive=True)[0]
open(p,'w').write(J)
m='android/app/src/main/AndroidManifest.xml'
x=open(m).read()
if 'supportsPictureInPicture' not in x:
    x=x.replace('<activity','<activity android:supportsPictureInPicture="true"',1)
open(m,'w').write(x)
print('patch ok')
