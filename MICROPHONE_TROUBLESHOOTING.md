# 🎤 Microphone & AirPods Troubleshooting Guide

## Issue: Voice Recognition Not Picking Up Audio

### Symptoms
- Green microphone shows "Listening..."
- Yellow warning: "⚠️ No audio input detected"
- Console shows `[Voice] Started listening...` but no audio events
- No `🎤 Audio input detected!` or `🗣️ Speech detected!` in console

## Root Cause

The Web Speech API is active, but the browser is not receiving audio from your microphone/AirPods. This is usually a **system-level or browser permission issue**, not a bug in the app.

## 🔍 Diagnostic Steps

### Step 1: Check Console Logs

Open browser console (F12) and look for these events:

**✅ Good (Working):**
```
[Voice] Started listening...
[Voice] 🎤 Audio input detected! Browser is receiving sound.
[Voice] 🔊 Sound detected from microphone.
[Voice] 🗣️ Speech detected! Processing...
[Voice] Got result event, results length: 1
[Voice] Result: hello world isFinal: true
```

**❌ Bad (Not Working):**
```
[Voice] Started listening...
(no other events when you speak)
```

### Step 2: Visual Indicators

The UI now shows real-time feedback:

| Indicator | Meaning | Status |
|-----------|---------|--------|
| 🎤 Listening... | Recognition active | ✅ API running |
| 🔊 Sound detected | Browser hears audio | ✅ Mic working |
| 🗣️ Speech detected! | Processing speech | ✅ Recognition working |
| ⚠️ No audio input | No sound from mic | ❌ Problem |
| Yellow warning box | Mic issue detected | ❌ Troubleshoot needed |

## 🛠️ Solutions

### Solution 1: Check System Audio Input (Most Common)

**Windows:**
1. Right-click speaker icon in taskbar
2. Click "Sound settings"
3. Under "Input", select your **AirPods** from dropdown
4. Speak and watch the blue bar move (testing mic)
5. If no movement, AirPods mic is not active

**macOS:**
1. System Settings → Sound → Input
2. Select **AirPods** from list
3. Speak and watch input level bars move
4. If no movement, reconnect AirPods

**The Problem:** Your system might be using the wrong input device (laptop mic instead of AirPods)

### Solution 2: Browser Microphone Permissions

**Chrome/Edge:**
1. Click the 🔒 lock icon in address bar
2. Find "Microphone" permission
3. Should say "Allowed" - if not, change it
4. Reload the page
5. Allow microphone when prompted

**Or go to settings:**
```
chrome://settings/content/microphone
```
- Ensure site is under "Allowed"
- Check default microphone is AirPods

### Solution 3: AirPods Connection Issues

**Reconnect AirPods:**
1. Put AirPods in case
2. Close case for 5 seconds
3. Open case and reconnect
4. Go to System Settings → Bluetooth
5. Ensure AirPods show "Connected" with microphone icon

**Check AirPods Mode:**
- AirPods Pro: Ensure not in "Off" mode for mic
- Some AirPods models default to phone mic only
- Try using just ONE AirPod (forces mic to that side)

### Solution 4: Test Microphone Outside Browser

**Windows:**
1. Settings → System → Sound → Input
2. Select AirPods
3. Click "Test your microphone"
4. Speak - should see blue bar moving

**macOS:**
1. QuickTime Player → File → New Audio Recording
2. Select AirPods as input
3. Click record and speak
4. If this doesn't work, problem is system-level

**If system test fails:** AirPods mic is not working at OS level

### Solution 5: Browser-Specific Issues

**Chrome/Edge Specific:**
1. Restart browser completely (close all windows)
2. Clear cache: `chrome://settings/clearBrowserData`
3. Check for browser updates
4. Try Incognito mode (rules out extensions)

**Safari Specific:**
1. Safari → Settings → Websites → Microphone
2. Ensure site has "Allow" permission
3. Try clearing website data

### Solution 6: Bluetooth Audio Delay

AirPods sometimes have a delay switching to microphone mode:

1. **Wait 3-5 seconds** after connecting before speaking
2. Play some audio first (activates Bluetooth)
3. Then try voice input
4. Sometimes takes a moment for mic to activate

### Solution 7: Use Different Audio Input

**Temporary workaround:**
1. Use laptop's built-in microphone instead
2. Or use wired headphones with mic
3. Test if voice recognition works with different input

**If laptop mic works but AirPods don't:** Bluetooth mic issue

## 🔬 Advanced Debugging

### Check MediaDevices API

Open browser console and run:

```javascript
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    console.log('Available devices:');
    devices.forEach(device => {
      console.log(device.kind, ':', device.label);
    });
  });
```

**Look for:**
```
audioinput : AirPods (Bluetooth)
audioinput : Built-in Microphone
```

If AirPods not listed, they're not recognized by browser.

### Test Microphone Access

```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    console.log('✅ Microphone access granted!');
    console.log('Active tracks:', stream.getAudioTracks());
    stream.getTracks().forEach(track => {
      console.log('Track label:', track.label);
      console.log('Track enabled:', track.enabled);
      track.stop();
    });
  })
  .catch(err => {
    console.error('❌ Microphone access failed:', err);
  });
```

### Check Recognition State

```javascript
// In browser console while on interview page
console.log('Recognition state:', window.speechRecognition);
```

## 📊 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "Listening..." but no audio | Wrong input device selected | Select AirPods in System Settings |
| Mic works in system test but not browser | Browser permission issue | Allow mic in browser settings |
| Works with laptop mic, not AirPods | Bluetooth audio profile | Disconnect/reconnect AirPods |
| Intermittent audio detection | AirPods battery low | Charge AirPods |
| No permission prompt shown | Permission already denied | Reset site permissions |
| Works in Incognito, not normal | Extension blocking | Disable extensions |

## 🎯 Quick Checklist

Run through this checklist:

- [ ] AirPods are connected to computer
- [ ] AirPods selected as **input device** in System Settings
- [ ] Test microphone in System Settings (see bars moving)
- [ ] Browser has microphone permission
- [ ] Site is allowed to use microphone
- [ ] No extension blocking microphone
- [ ] AirPods have sufficient battery
- [ ] Tried speaking loudly and clearly
- [ ] Waited 5 seconds after connecting
- [ ] Reloaded the page after granting permission

## 🆘 Still Not Working?

### Try Alternative Approaches

1. **Use Text Input:**
   - Toggle microphone OFF (gray button)
   - Type your answer manually
   - Click Submit

2. **Use Laptop Microphone:**
   - Switch input device to built-in mic
   - Test if voice recognition works
   - Isolates AirPods as the issue

3. **Try Different Browser:**
   - Chrome/Edge work best
   - Safari works on Mac
   - Firefox has limited support

4. **Check Operating System:**
   - Windows: Some Bluetooth drivers have issues
   - macOS: Usually works better with AirPods
   - Update Bluetooth drivers

## 🔧 System-Specific Fixes

### Windows 11/10

**Enable Microphone Privacy:**
1. Settings → Privacy → Microphone
2. Toggle "Allow apps to access your microphone" → **ON**
3. Scroll down, ensure Chrome/Edge is allowed

**Update Bluetooth Drivers:**
1. Device Manager → Bluetooth
2. Right-click Bluetooth adapter → Update driver
3. Restart computer

### macOS

**Reset Microphone Permissions:**
```bash
# In Terminal
tccutil reset Microphone
```
Then reopen browser and grant permission again.

**Check AirPods Firmware:**
- Settings → Bluetooth → (i) next to AirPods
- Ensure firmware is up to date

## 📝 What to Check in Console

When you speak, you should see:

```
1. [Voice] Started listening...
   ↓
2. [Voice] 🎤 Audio input detected!
   ↓
3. [Voice] 🔊 Sound detected from microphone.
   ↓
4. [Voice] 🗣️ Speech detected! Processing...
   ↓
5. [Voice] Got result event, results length: 1
   ↓
6. [Voice] Result: your text here isFinal: true
   ↓
7. [Voice] Final transcript: your text here
```

**If you only see step 1:** Microphone is not sending audio to browser.

## 🎤 AirPods Pro Specific

**Microphone Mode:**
- AirPods Pro have multiple mic modes
- Ensure not set to "Off" in Bluetooth settings
- Try switching between "Automatic" and "Always Left/Right"

**Transparency Mode:**
- Some users report better recognition with Transparency ON
- Try toggling between Noise Cancellation and Transparency

## ⚙️ Browser Settings URLs

**Chrome:**
- General settings: `chrome://settings/`
- Microphone: `chrome://settings/content/microphone`
- Site permissions: `chrome://settings/content/siteDetails?site=http://localhost:3000`

**Edge:**
- Same as Chrome (Chromium-based)

**Safari:**
- Safari → Settings → Websites → Microphone

## 🚀 After Fixing

Once microphone works, you should see:

1. ✅ Green pulsing microphone icon
2. ✅ "🎤 Listening..." message
3. ✅ "🔊 Sound detected" when you make noise
4. ✅ "🗣️ Speech detected!" when you speak
5. ✅ Words appearing in text field as you speak

## 📞 Last Resort: Type Your Answers

If voice input continues to fail:

1. Click the green microphone button to turn voice **OFF**
2. Type your answers in the text field
3. Click Submit as normal
4. The app works perfectly in text-only mode

**Voice input is a convenience feature, not required!**

---

## Summary

**Most Common Fix:** Select AirPods as input device in System Settings, then reload the page.

**Second Most Common:** Allow microphone permission in browser (click 🔒 in address bar).

**Third Most Common:** Reconnect AirPods (Bluetooth connection issue).

---

**If none of this works, use text input mode. The interview functionality is identical.** ✅

