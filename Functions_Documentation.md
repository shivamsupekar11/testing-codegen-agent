# Logix Framework — API Documentation

> **Package:** `com.logix.framework`
> **Version:** 1.0
> **Last Updated:** 2026-02-12

---

## Table of Contents

1. [LogixTestInterface](#1-logixtestinterface)
   - [Lifecycle](#lifecycle)
   - [Element Verification](#element-verification)
   - [Text Input & Retrieval](#text-input--retrieval)
   - [Click & Navigation](#click--navigation)
   - [Scrolling & Swiping](#scrolling--swiping)
   - [Screenshot & Reporting](#screenshot--reporting)
   - [Page State](#page-state)
   - [Dropdown & Radio Button](#dropdown--radio-button)
   - [Window Management](#window-management)
   - [iFrame Handling](#iframe-handling)
   - [Hover & Mouse Actions](#hover--mouse-actions)
   - [Element Lists](#element-lists)
   - [Network & Video](#network--video)
   - [Link Validation](#link-validation)
   - [Utility](#utility)
2. [WebAutomationDriverImpl](#2-webautomationdriverimpl)
3. [Full End-to-End Usage Example](#3-full-end-to-end-usage-example)

---

## 1. `LogixTestInterface`

**File:** `framework/src/main/java/com/logix/framework/api/LogixTestInterface.java`
**Type:** `interface`

### Summary

`LogixTestInterface` is the **top-level contract** for all automation drivers within the Logix framework. It defines a unified, platform-agnostic API that every driver implementation (web, mobile, TV, etc.) must support. Every method carries a `default` no-op or stub implementation, so platform-specific drivers only need to override the methods that apply to their platform.

Test classes extend `LogixBaseTestDriver` and access all methods via the `logixTestInterface` field.

---

### Inner Interface — `Listener`

| Method | Params | Description |
|---|---|---|
| `onConnect()` | — | Invoked when the driver is successfully connected. |
| `onError(int errorCode, String message)` | `errorCode` – numeric error identifier<br>`message` – human-readable description | Invoked when a connection or runtime error occurs. |

---

### Lifecycle

---

#### `connect()`

| Attribute | Detail |
|---|---|
| **Summary** | Initializes the automation driver and establishes a session with the target platform (browser, device, etc.). |
| **Input Params** | *None* |
| **Output** | `void` |
| **Throws** | `LogixException` — if the connection fails or the driver is already initialized. |
| **Usage Example** | ```java
logixTestInterface.connect();
``` |

---

#### `teardown()`

| Attribute | Detail |
|---|---|
| **Summary** | Gracefully shuts down the driver, closing any open sessions and releasing resources. |
| **Input Params** | *None* |
| **Output** | `void` |
| **Throws** | `LogixException` |
| **Usage Example** | ```java
logixTestInterface.teardown();
``` |

---

#### `isDriverInitialized()`

| Attribute | Detail |
|---|---|
| **Summary** | Checks whether the driver has been initialized and is ready for interactions. |
| **Input Params** | *None* |
| **Output** | `boolean` — `true` if the driver is initialized, `false` otherwise. |
| **Usage Example** | ```java
if (logixTestInterface.isDriverInitialized()) {
    // proceed with test
}
``` |

---

#### `getSessionId()`

| Attribute | Detail |
|---|---|
| **Summary** | Returns the unique session identifier of the current driver session. |
| **Input Params** | *None* |
| **Output** | `String` — the session ID, or `null` if no session is active. |
| **Usage Example** | ```java
String sessionId = logixTestInterface.getSessionId();
System.out.println("Session: " + sessionId);
``` |

---

#### `getCurrentPackage()`

| Attribute | Detail |
|---|---|
| **Summary** | *(Mobile-specific)* Returns the current foreground package/bundle identifier. |
| **Input Params** | *None* |
| **Output** | `String` — package name, or `null`. |

---

### Element Verification

---

#### `checkElement(String xpath, String successMsg, String failMsg)`

| Attribute | Detail |
|---|---|
| **Summary** | Waits for an element identified by XPath to be present in the DOM and logs a success or failure message. |
| **Input Params** | `xpath` (`String`) — XPath of the target element.<br>`successMsg` (`String`) — message logged if the element is found.<br>`failMsg` (`String`) — message logged if the element is not found within the timeout. |
| **Output** | `boolean` — `true` if the element is present, `false` otherwise. |
| **Usage Example** | ```java
boolean found = logixTestInterface.checkElement(
    "//button[@id='login']",
    "PASS: Login button found",
    "FAIL: Login button NOT found"
);
Assert.assertTrue(found, "Expected element not found on page");
``` |

---

#### `isEnabledElement(String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Checks whether the element is enabled (not disabled). |
| **Input Params** | `xPath` (`String`) — XPath of the target element. |
| **Output** | `boolean` — `true` if the element is enabled. |
| **Usage Example** | ```java
boolean editable = logixTestInterface.isEnabledElement("//input[@id='name']")
    && logixTestInterface.getAttribute("//input[@id='name']", "readonly") == null;
System.out.println("Field is editable: " + editable);
``` |

---

### Text Input & Retrieval

---

#### `setText(String inputString, String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Types the given text into the element located by XPath. Clears existing content first. |
| **Input Params** | `inputString` (`String`) — the text to type.<br>`xPath` (`String`) — XPath of the target input element. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.setText("admin@example.com", "//input[@id='email']");
logixTestInterface.setText("secretPassword", "//input[@type='password']");
``` |

---

#### `getText(String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Returns the visible text of the element located by XPath. |
| **Input Params** | `xPath` (`String`) — XPath of the target element. |
| **Output** | `String` — the visible text, or `null`. |
| **Usage Example** | ```java
String statusText = logixTestInterface.getText("//div[@class='status']//span");
System.out.println("Status: " + statusText);
``` |

---

#### `getAttribute(String xPath, String attribute)`

| Attribute | Detail |
|---|---|
| **Summary** | Returns the value of a specific HTML attribute of the element. |
| **Input Params** | `xPath` (`String`) — XPath of the target element.<br>`attribute` (`String`) — attribute name (e.g. `"href"`, `"class"`, `"readonly"`). |
| **Output** | `String` — attribute value, or `null` if not present. |
| **Usage Example** | ```java
String readonlyAttr = logixTestInterface.getAttribute("//input[@id='email']", "readonly");
boolean isReadonly = readonlyAttr != null;
``` |

---

### Click & Navigation

---

#### `pressEnter(int count, long delayMs)`

| Attribute | Detail |
|---|---|
| **Summary** | Sends an Enter/click action the specified number of times with a delay between each. |
| **Input Params** | `count` (`int`) — number of times to press/click.<br>`delayMs` (`long`) — pause in milliseconds between presses. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.pressEnter(1, 0);
``` |

---

#### `pressEnter(int count, long delayMs, String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Clicks the element at the given XPath `count` times with a delay between clicks. Includes a **JS-click fallback** when standard click is intercepted, and **element highlighting** for visual debugging. |
| **Input Params** | `count` (`int`) — number of clicks.<br>`delayMs` (`long`) — pause in milliseconds between clicks.<br>`xPath` (`String`) — XPath of the element to click. |
| **Output** | `void` |
| **Usage Example** | ```java
// Click a button once
logixTestInterface.pressEnter(1, 0, "//button[@type='submit']");

// Click a menu item with delay
logixTestInterface.pressEnter(1, 100, "//a[normalize-space()='MOVIES']");
``` |

---

#### `tapOnCenter(String xpath)`

| Attribute | Detail |
|---|---|
| **Summary** | *(Mobile-specific)* Taps on the center of the element identified by XPath. |
| **Input Params** | `xpath` (`String`) — XPath of the target element. |
| **Output** | `void` |

---

#### `navigateToUrl(String url)`

| Attribute | Detail |
|---|---|
| **Summary** | Navigates the browser to the specified URL. |
| **Input Params** | `url` (`String`) — the full URL to open. |
| **Output** | `void` |
| **Throws** | `UnsupportedOperationException` if not implemented by the driver. |
| **Usage Example** | ```java
logixTestInterface.navigateToUrl("https://dev.erosnow.com/");
logixTestInterface.waitForPageReady(10);
``` |

---

#### `goBack(int count, long delayMs)`

| Attribute | Detail |
|---|---|
| **Summary** | Navigates back (browser back or device back) a specified number of times. |
| **Input Params** | `count` (`int`) — how many times to go back.<br>`delayMs` (`long`) — pause in milliseconds between each back action. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.goBack(1, 100);
logixTestInterface.goBack(2, 500);
``` |

---

#### `refreshPage()`

| Attribute | Detail |
|---|---|
| **Summary** | Refreshes the current page and waits for `document.readyState === 'complete'`. |
| **Input Params** | *None* |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.refreshPage();
``` |

---

#### `getCurrentURL()`

| Attribute | Detail |
|---|---|
| **Summary** | Returns the URL currently loaded in the browser. |
| **Input Params** | *None* |
| **Output** | `String` — current URL, or `null`. |
| **Usage Example** | ```java
String currentUrl = logixTestInterface.getCurrentURL();
Assert.assertTrue(currentUrl.contains("/genres"), "URL does not contain '/genres'");
``` |

---

#### `pressArrowKey(Keys key)`

| Attribute | Detail |
|---|---|
| **Summary** | Sends a keyboard arrow key press globally (not targeted to a specific element). |
| **Input Params** | `key` (`Keys`) — the Selenium `Keys` constant (e.g. `Keys.ARROW_DOWN`, `Keys.ARROW_RIGHT`). |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.pressArrowKey(Keys.ARROW_RIGHT);
logixTestInterface.pressArrowKey(Keys.ARROW_DOWN);
``` |

---

### Scrolling & Swiping

---

#### `goDown(int count, long delayMs)`

| Attribute | Detail |
|---|---|
| **Summary** | Scrolls or swipes downward a specified number of times with a delay between each action. |
| **Input Params** | `count` (`int`) — number of scroll/swipe actions.<br>`delayMs` (`long`) — pause in milliseconds between each action. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.goDown(5, 800);
``` |

---

#### `goDown(int maxSwipes, long delay, String xpath)`

| Attribute | Detail |
|---|---|
| **Summary** | Scrolls downward until the target XPath element is found, up to `maxSwipes` times. |
| **Input Params** | `maxSwipes` (`int`) — maximum number of scroll actions.<br>`delay` (`long`) — pause in milliseconds between each action.<br>`xpath` (`String`) — XPath of the target element to scroll towards. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.goDown(10, 500, "//div[@id='footer']");
``` |

---

#### `goUp(int count, long delayMs)` / `goUp(int count, long delayMs, String xpath)`

| Attribute | Detail |
|---|---|
| **Summary** | Scrolls or swipes upward. Same semantics as `goDown` but in the opposite direction. |
| **Input Params** | Same as `goDown`. |
| **Output** | `void` |

---

#### `goLeft(int count, long delayMs)` / `goLeft(int count, long delayMs, String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Scrolls or swipes left. Useful for horizontal carousels and rails. |
| **Input Params** | Same as `goDown`. |
| **Output** | `void` |

---

#### `goRight(int count, long delayMs)` / `goRight(int count, long delayMs, String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Scrolls or swipes right. Useful for horizontal carousels and rails. |
| **Input Params** | Same as `goDown`. |
| **Output** | `void` |

---

#### `scrollToCardView(int maxScrolls, String railxPath, String cardViewXpath, String textOnCard)`

| Attribute | Detail |
|---|---|
| **Summary** | Scrolls within a rail/carousel to locate and bring a specific card into view. Can be used to simply scroll to a rail element or to find a specific card by text. |
| **Input Params** | `maxScrolls` (`int`) — maximum number of horizontal swipes.<br>`railxPath` (`String`) — XPath of the rail/target element to scroll to.<br>`cardViewXpath` (`String`) — XPath of individual card views (can be empty `""`).<br>`textOnCard` (`String`) — the text to match on the card (can be empty `""`). |
| **Output** | `void` |
| **Usage Example** | ```java
// Scroll to a rail element
logixTestInterface.scrollToCardView(10, "//div[normalize-space()='Movies']", "", "");

// Scroll within a rail to find a specific card
logixTestInterface.scrollToCardView(10,
    "//a[normalize-space()='Flashback 90s']",
    "//img[contains(@class, 'l-img') and contains(@alt, 'Himmatvar')]",
    "");
``` |

---

#### `scrollToFooter(String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Scrolls to the bottom of the page multiple times to trigger lazy-loading, then waits for the footer element to appear and centers it in view. |
| **Input Params** | `xPath` (`String`) — XPath of the footer element. |
| **Output** | `void` |
| **Usage Example** | ```java
String helpCenter = "//a[@class='footer-playlist-link'][normalize-space()='Help Center']";
logixTestInterface.scrollToFooter(helpCenter);
logixTestInterface.pressEnter(1, 100, helpCenter);
``` |

---

### Screenshot & Reporting

---

#### `takeScreenshot(String stepname)`

| Attribute | Detail |
|---|---|
| **Summary** | Captures a screenshot and attaches it to the Extent report with the given label. |
| **Input Params** | `stepname` (`String`) — descriptive label for the screenshot in the report. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.takeScreenshot("login_page_loaded");
logixTestInterface.takeScreenshot("after_email_validation");
``` |

---

#### `takeScreenshot(String stepname, String xpath)`

| Attribute | Detail |
|---|---|
| **Summary** | Captures a screenshot focused on a specific element. |
| **Input Params** | `stepname` (`String`) — label for the screenshot in the report.<br>`xpath` (`String`) — XPath of the element to focus on. |
| **Output** | `void` |

---

### Page State

---

#### `waitForPageReady(int timeInSeconds)`

| Attribute | Detail |
|---|---|
| **Summary** | Blocks execution until `document.readyState === 'complete'` or the timeout expires. |
| **Input Params** | `timeInSeconds` (`int`) — maximum wait time in seconds. |
| **Output** | `boolean` — `true` if the page becomes ready within the timeout. |
| **Usage Example** | ```java
logixTestInterface.navigateToUrl("https://dev.erosnow.com/");
logixTestInterface.waitForPageReady(10);
``` |

---

### Dropdown & Radio Button

---

#### `clickDropdownOptions(String xPath, String xpath1)`

| Attribute | Detail |
|---|---|
| **Summary** | Opens a dropdown/menu by clicking the trigger element, then iterates through and clicks each visible dropdown option. Takes a screenshot after each click and waits for the page to load. |
| **Input Params** | `xPath` (`String`) — XPath of the trigger element (tab, menu, button).<br>`xpath1` (`String`) — XPath of the dropdown option list or a specific dropdown option. |
| **Output** | `void` |
| **Usage Example** | ```java
// Click through all dropdown options under a menu
logixTestInterface.clickDropdownOptions(
    "//a[normalize-space()='ORIGINALS']",
    "//ul[contains(@class,'hm-dd-content')]//a[@class='menu-link']"
);

// Click a specific dropdown option
String monthOption = "//div[@id='profile-settings']//select[1]";
String month = "//select//option[@value='03']";
logixTestInterface.clickDropdownOptions(monthOption, month);
``` |

---

#### `getSelectedDropdownText(String dropdownXpath)`

| Attribute | Detail |
|---|---|
| **Summary** | Returns the text of the currently selected option in a `<select>` dropdown. |
| **Input Params** | `dropdownXpath` (`String`) — XPath of the `<select>` element. |
| **Output** | `String` — trimmed text of the selected option. |
| **Usage Example** | ```java
String selected = logixTestInterface.getSelectedDropdownText("//select[@id='country']");
System.out.println("Selected: " + selected);
``` |

---

#### `getRadioButtonSelectedValue(String containerClassxPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Returns the `value` attribute of the currently selected radio button within a container element. |
| **Input Params** | `containerClassxPath` (`String`) — CSS selector of the container holding radio buttons. |
| **Output** | `String` — the selected radio button's value, or `null` if none is selected. |

---

#### `setRadioButtonValue(String containerClassxPath, String value)`

| Attribute | Detail |
|---|---|
| **Summary** | Selects a radio button by clicking its label text within a container. Includes stale-element retry logic (up to 3 retries). |
| **Input Params** | `containerClassxPath` (`String`) — XPath of the radio group container.<br>`value` (`String`) — label text of the radio option to select. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.setRadioButtonValue("//div[@class='gender-group']", "Male");
``` |

---

#### `getRadioButtonSelected(String inputName)`

| Attribute | Detail |
|---|---|
| **Summary** | Finds the selected radio button by the HTML `name` attribute and prints the selected value to console. |
| **Input Params** | `inputName` (`String`) — the `name` attribute of the radio input group. |
| **Output** | `void` (prints selected value to console). |
| **Usage Example** | ```java
logixTestInterface.getRadioButtonSelected("gender");
// Console: "Selected gender: M"
``` |

---

#### `setRadioButton(String radioButtonName, String value)`

| Attribute | Detail |
|---|---|
| **Summary** | Selects a radio button by matching the `name` attribute and the `value` attribute. |
| **Input Params** | `radioButtonName` (`String`) — the `name` attribute of the radio group.<br>`value` (`String`) — the `value` attribute of the radio to select. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.setRadioButton("gender", "M");
logixTestInterface.getRadioButtonSelected("gender");
``` |

---

### Window Management

---

#### `getAllWindowHandles()`

| Attribute | Detail |
|---|---|
| **Summary** | Returns all open window/tab handles. |
| **Input Params** | *None* |
| **Output** | `Set<String>` — set of window handle strings. |

---

#### `getParentWindowHandle()`

| Attribute | Detail |
|---|---|
| **Summary** | Returns the handle of the current/parent window. |
| **Input Params** | *None* |
| **Output** | `String` — the window handle. |

---

#### `switchToWindow(String childWindow)`

| Attribute | Detail |
|---|---|
| **Summary** | Switches driver control to the specified window/tab handle. |
| **Input Params** | `childWindow` (`String`) — the window handle to switch to. |
| **Output** | `void` |

---

#### `closeWindow()`

| Attribute | Detail |
|---|---|
| **Summary** | Closes the current window/tab. |
| **Input Params** | *None* |
| **Output** | `void` |

**Combined Usage Example:**
```java
String parent = logixTestInterface.getParentWindowHandle();
Set<String> handles = logixTestInterface.getAllWindowHandles();

for (String h : handles) {
    if (!h.equals(parent)) {
        logixTestInterface.switchToWindow(h);
        break;
    }
}
// do work in child window
logixTestInterface.closeWindow();
logixTestInterface.switchToWindow(parent);
```

---

### iFrame Handling

---

#### `switchToFrame(String iframeXpath)`

| Attribute | Detail |
|---|---|
| **Summary** | Switches the driver context into an iframe located by XPath. Waits up to 10 seconds for the iframe to be present. |
| **Input Params** | `iframeXpath` (`String`) — XPath of the iframe element. |
| **Output** | `void` |

---

#### `switchToDefaultContent()`

| Attribute | Detail |
|---|---|
| **Summary** | Switches the driver context back to the main document (out of any iframe). |
| **Input Params** | *None* |
| **Output** | `void` |

**Combined Usage Example:**
```java
logixTestInterface.switchToFrame("//iframe[@id='payment']");
logixTestInterface.setText("4111111111111111", "//input[@name='card']");
logixTestInterface.switchToDefaultContent();
```

---

### Hover & Mouse Actions

---

#### `hoverOnWebElementByxPath(String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Moves the mouse over the element identified by XPath (hover action). Commonly used before clicking dropdown menus. |
| **Input Params** | `xPath` (`String`) — XPath of the target element. |
| **Output** | `void` |
| **Usage Example** | ```java
// Hover on a menu to reveal dropdown
logixTestInterface.hoverOnWebElementByxPath("//a[normalize-space()='MOVIES']");
// Then click a sub-menu item
logixTestInterface.pressEnter(1, 100, "//a[contains(text(),'Genres')]");
``` |

---

#### `hoverByOffset(int x, int y)`

| Attribute | Detail |
|---|---|
| **Summary** | Moves the mouse by pixel offsets from the current position. Useful for dismissing hovers or tooltips. |
| **Input Params** | `x` (`int`) — horizontal offset in pixels.<br>`y` (`int`) — vertical offset in pixels. |
| **Output** | `void` |
| **Usage Example** | ```java
// Hover away to dismiss a dropdown
logixTestInterface.hoverByOffset(300, 300);
``` |

---

### Element Lists

---

#### `getElementsList(String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Returns all `WebElement` objects matching the given XPath. |
| **Input Params** | `xPath` (`String`) — XPath locator. |
| **Output** | `List<WebElement>` — the matching elements. |
| **Usage Example** | ```java
List<WebElement> links = logixTestInterface.getElementsList("//a[@class='menu-link']");
System.out.println("Found " + links.size() + " links");
``` |

---

#### `listOfElemnt(String xPath)`

| Attribute | Detail |
|---|---|
| **Summary** | Returns the visible text strings of all non-empty elements matching the XPath. |
| **Input Params** | `xPath` (`String`) — XPath locator. |
| **Output** | `List<String>` — list of visible text strings (empty texts are excluded). |
| **Usage Example** | ```java
List<String> railTitles = logixTestInterface.listOfElemnt("//a[@class='pl-anchor-heading']");
int cnt = 1;
for (String title : railTitles) {
    System.out.println(cnt++ + " : " + title);
}
``` |

---

### Network & Video

---

#### `setNetworkOffline(boolean isOffline)`

| Attribute | Detail |
|---|---|
| **Summary** | *(Chromium-only)* Enables or disables network connectivity using the Chrome DevTools Protocol (CDP). Useful for offline-mode testing. |
| **Input Params** | `isOffline` (`boolean`) — `true` to simulate offline, `false` to restore connectivity. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.setNetworkOffline(true);
// perform offline assertions
logixTestInterface.setNetworkOffline(false);
``` |

---

#### `isVideoPlayingInFullScreen()`

| Attribute | Detail |
|---|---|
| **Summary** | Checks if an HTML5 `<video>` element is currently playing in fullscreen mode via JavaScript. |
| **Input Params** | *None* |
| **Output** | `boolean` — `true` if a video is actively playing in fullscreen. |
| **Usage Example** | ```java
boolean isPlaying = logixTestInterface.isVideoPlayingInFullScreen();
Assert.assertTrue(isPlaying, "Video is not playing in fullscreen");
``` |

---

### Link Validation

---

#### `checkBrokenLinks()`

| Attribute | Detail |
|---|---|
| **Summary** | Scans all `<a>` tags on the current page and verifies each `href` returns an HTTP status < 400. Logs broken links and links with empty/null `href` to console. |
| **Input Params** | *None* |
| **Output** | `void` (results are printed to console). |
| **Usage Example** | ```java
logixTestInterface.navigateToUrl("https://dev.erosnow.com/");
logixTestInterface.waitForPageReady(10);
logixTestInterface.checkBrokenLinks();
``` |

---

### Utility

---

#### `sleepQuietly(long millis)`

| Attribute | Detail |
|---|---|
| **Summary** | Pauses execution for the given number of milliseconds. Properly handles `InterruptedException`. |
| **Input Params** | `millis` (`long`) — time to sleep in milliseconds. |
| **Output** | `void` |
| **Usage Example** | ```java
logixTestInterface.sleepQuietly(2000);  // wait 2 seconds
``` |

---

#### App Lifecycle *(Mobile-specific)*

| Method | Summary |
|---|---|
| `clearCache()` | Clears the application / browser cache. |
| `exitApp()` | Exits the application under test. |
| `installApp()` | Installs the application under test. |
| `uninstallApp()` | Uninstalls the application under test. |

---

#### Charles Proxy

| Method | Summary |
|---|---|
| `connectCharles()` | Connects a Charles Proxy session for network debugging. |
| `disConnectCharles()` | Disconnects the Charles Proxy session. |

---

---

## 2. `WebAutomationDriverImpl`

**File:** `framework/src/main/java/com/logix/framework/impl/web/WebAutomationDriverImpl.java`
**Type:** `class`

### Summary

`WebAutomationDriverImpl` is the **concrete web-browser implementation** that provides the actual behavior for the methods defined in `LogixTestInterface`. It manages the Selenium `WebDriver` lifecycle in a **thread-safe** manner (using `ThreadLocal`) and implements element interaction, scrolling, screenshots, network emulation, and more.

> **Note:** Test classes do NOT use this class directly. All interaction goes through `logixTestInterface`. This class is documented here for framework developers and maintainers.

### Key Characteristics

| Feature | Detail |
|---|---|
| **Thread Safety** | `WebDriver` instances are stored per-thread via `ThreadLocal`, enabling parallel test execution. |
| **Browser Support** | Chrome, Firefox, Safari, Edge (configurable via `LogixTestConfig` param `"browser"`). |
| **Smart Click** | Click operations include a JS-click fallback when the standard click is intercepted by overlays. |
| **Element Highlighting** | Interacted elements are highlighted with a `3px solid red` border for visual debugging. |
| **Scroll Controller** | Delegates directional scrolling to `WebScrollControllerImpl`. |
| **Reporting** | Screenshots are automatically saved and attached to the Extent report via `ExtentReportListener`. |

### Constructor

```java
public WebAutomationDriverImpl(LogixTestConfig config, LogixTestInterface.Listener listener)
```

| Param | Type | Description |
|---|---|---|
| `config` | `LogixTestConfig` | Configuration object. Key param: `config.getParam("browser", "chrome")` — one of `chrome`, `firefox`, `safari`, `edge`. |
| `listener` | `LogixTestInterface.Listener` | Callback for connect/error events. Can be `null`. |

### Constants

| Constant | Value | Description |
|---|---|---|
| `DEFAULT_IMPLICIT_WAIT_SECONDS` | `5` | Default implicit wait timeout applied to the WebDriver. |
| `DEFAULT_PAGELOAD_TIMEOUT_SECONDS` | `30` | Default page-load timeout applied to the WebDriver. |
| `MAX_SCROLL_ATTEMPTS` | `20` | Maximum scroll steps when searching for an element via `scrollToElement`. |
| `SCROLL_STEP_PIXELS` | `500` | Pixels scrolled per step in `scrollToElement()`. |
| `SCROLL_RETRY_DELAY_MILLIS` | `800` | Delay in milliseconds between scroll retries. |

### Additional Implementation Methods

These methods exist on the implementation class but are **not part of the interface**. They are useful for framework extension:

| Method | Summary |
|---|---|
| `getWebDriver()` | Returns `Optional<WebDriver>` for the current thread. |
| `getActiveDriver()` | Returns the active `WebDriver`; throws `IllegalStateException` if not initialized. |
| `stop()` | Quits the WebDriver and cleans up all ThreadLocal references. |
| `waitForVisible(driver, locator, timeoutSeconds)` | Explicitly waits for an element to be visible. Returns the `WebElement`. |
| `clickElement(driver, locator)` / `clickElement(locator)` | Locates, highlights, clicks (with JS fallback), and unhighlights an element. |
| `type(driver, locator, text)` / `type(locator, text)` | Clears the field and types text (internal implementation of `setText`). |
| `getText(driver, locator)` / `getText(locator)` | Returns visible text of an element by `By` locator. |
| `highlightElement(driver, element)` | Adds a red border to an element for visual debugging. |
| `removeHighlight(driver, element)` | Restores the element's original style. |
| `scrollToElement(driver, railLocator)` / `scrollToElement(railLocator)` | Scrolls step-by-step until the element is found, then centers it. |

*© 2025 Logituit. All rights reserved.*
