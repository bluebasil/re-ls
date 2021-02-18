var app = null;


var registered_functions = [] // allows registering to updates to the underlying payload
var loaded_dir = {}           // saves the last response payload
var loading = true            // tracks the current state of the reqeust call - not currently used
var last_timer = null         // tracks the last timeer so that it can be aborted

/**
 * intialPath - pulls the inital path out of the url request,
 *   otherwise return the default initial path of `.`
 *
 * @return {stirng} The inital path to use
 */
function initialPath() {
  // Default current path to '.'
  var default_path = "."
  // Check to see if there was a privided starting path
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('b64path')) {
    // We are decrypting the path becuse this function is expected to retrn a string
    default_path = atob(urlParams.get('b64path'))
  }
  return default_path
}

/**
 * makeRequest - redirecs the current path to the path parameter.
 *   then calls the functions listening to the response return
 *
 * @param {string} path - The path to the requested destination
 */
function makeRequest(path) {
  // abort any existing timeout - don't want to disrupt the page as it's loading
  if (last_timer != null) {
    window.clearTimeout(last_timer)
  }

  // base 64 encodes the recived path and formulates the API call
  encoded = btoa(path)
  resultingUrl = 'http://127.0.0.1:5000/ls?b64path=' + encoded
  console.log("Making API request: " + resultingUrl)
  // set loading to true between call and response - not currently used however
  loading = true
  // make API request, with appropriate callbacks
  $.ajax({
    url: resultingUrl,
    type: 'GET',
    success: requestCallback,
    error: handleError
  })
}

/**
 * handleError - Extreemly basic error message.
 * Notably this is caused by attempting to navigate to a file that does not exist or not authorized
 *
 * TODO: make more user friendly
 */
function handleError(data) {
  console.log(data)
  alert(data.status + ": " + data.statusText)
}

/**
 * responseReturn - Helper function for the Request callbacks
 *   notifies all registered functions of the new payload
 *   Also sets a timer for pinging for a payload update if the payload does not have a done status
 */
function responseReturn(data,initial) {
  loaded_dir = JSON.parse(data)
  for (var i=0; i<registered_functions.length; i++) {
    registered_functions[i](loaded_dir, initial)
  }
  loading = false
  // This will casue the website to ping until the respince includes true in the done field
  if (!loaded_dir["done"]) {
    last_timer = setTimeout(pingForUpdate,1000)
  }
}

/**
 * requestCallback - used by makeRequest to process a good payload response
 */
function requestCallback(data) {
  console.log("Request returned.")
  responseReturn(data,true)
}

/**
 * pingForUpdate - Sets up the ping to get any payload updates, with the appropriate callbacks
 */
function pingForUpdate() {
  $.ajax({
    url: 'http://127.0.0.1:5000/ping',
    type: 'GET',
    success: pingCallback,
    error: handleError
  })
}

/**
 * pingCallback - a wrapper around responseReturn to process the responce, but noting that it is not an inital response (only a ping update)
 */
function pingCallback(data) {
  responseReturn(data,false)
}


/**
 * lsrow Vue component
 * renders a row in the table
 *
 * @prop {JsonObject} row - json object containing at least Name, Size, and `Last Modified`
 */
Vue.component('lsrow', {
    template: `
    <tr :class="getClass" v-on:click="selected">
      <td> <img v-if="isDir" src="dir_icon.ico" class="dir" /> </td>
      <td class="nameColumn"> {{ this.row.Name }} </td>
      <td class="size"> {{ this.row.Size }} </td>
      <td class="modified"> {{ this.row["Last Modified"] }} </td>
    </tr>
    `,
    methods: {
      /* onclick action of a directory should redirect to that directory */
      selected() {
        if (this.isDir) {
          makeRequest(this.row.path)
        }
      }
    },
    computed: {
      /* used to choose wether to render the folder icon */
      isDir: function() {
        if (this.row.Type === 'DIR') {
          return true
        }
        return false
      },
      /* a class of 'dir' allows hover annimations */
      getClass: function() {
        if (this.isDir) {
          return "dir"
        }
        return ""
      }
    },
    props: {
      row: {
        type: Object,
        required:true
        /* This should be a json object with the fields defined in tools.py */
      }
    }
})

/**
 * lstable - Vue component
 * Renders the table that contains the folder contents
 */
Vue.component('lstable', {
    template: `
        <table>
        <!-- adds the columns headers -->
        <tr>
          <th></th>
          <th>Name</th>
          <th>Size</th>
          <th>Last Modified</th>
        </tr>
        <lsrow v-for="r in rows" :row="r" />
        </table>
    `,
    data() {
        console.log("Registering table")
        registered_functions.push(this.save_data)
        // makes the inital call to the rels API
        makeRequest(initialPath())
        // Initalize no rows - should retrunn a blank table before anything has loaded
        return {rows:[]}
    },
    methods: {
      save_data: function(data, initial) {
        this.rows = data["contents"]
      }
    }
})

/**
 * buttoncomp - Vue component
 * basic button component for consistent formatting
 *
 * @prop {function} callback - function to call if the button is clicked
 * @prop {string} text       - text to write on the button
 * @prop {string} img        - local path to the image to put on the button
 */
Vue.component('buttoncomp', {
  template: `
    <div class="button" v-on:click="callback">
      <div ><img :src="img" class="button" /></div>
      <div class="buttonText"><span>{{ text }}</span></div>
    </div>
  `,
  props: {
    callback: {
      required: true
    },
    text: {
      type: String,
      required: true
    },
    img: {
      type: String
    }
  }
})

/**
 * lshead - Vue component
 * A single component for the header.  Could be split up better to better seperate components
 */
Vue.component('lshead', {
  template: `
    <div>
      <input type="text" id="searchbox" class="searchbox" @keyup.enter="goTo" @keyup="checkDiff">
      <buttoncomp :callback="goUpDir" text="Up Directory" img="up_dir.png" />
      <buttoncomp :callback="goTo" text="Go to Path" img="dir_icon.png" v-if="diff" />

      <div class="generalData"><div class="buttonText"><span>
      Total Size: {{ total_size }}  -  Count: {{ total_count }} </span></div></div>
    </div>
  `,
  data() {
    console.log("Registering searchbox")
    registered_functions.push(this.save_data)
    return {originalPath:"",
            diff: false,
            total_count: "...",
            total_size: "..."}
  },
  methods: {
    goUpDir: function() {
      upDir = loaded_dir["path"]

      // The most reliable way to go up a dir may be to simply append `..`
      // rels will clean up this path automatically
      // first we should add a slash if it's not already added
      if (upDir.substr(upDir.length - 1) != "/") {
        upDir += "/"
      }
      upDir += ".."
      // navigate to this new path
      makeRequest(upDir)
    },
    save_data: function(data, initial) {
      this.total_count = data.count
      this.total_size = data.Size

      // We only want to reset the search box value on the intial api call, not the subsequent pings
      if (initial) {
        this.originalPath = data.path
        document.getElementById("searchbox").value = this.originalPath
      }
      this.checkDiff()
    },
    goTo: function() {
      // When the goto button is clicked, naviage to the path specified by goto
      makeRequest(document.getElementById("searchbox").value)
    },
    checkDiff: function() {
      // Keeps track of if the searchbox has been modified  - with whihc we can show to goto button
      this.diff = (this.originalPath != document.getElementById("searchbox").value)
    }
  }
})

/**
 * dirpage - Vue components
 * Just for organizing the root components
 */
Vue.component('dirpage', {
  template: `
    <div>
    <lshead />

    <lstable />
    </div>
  `
})

app = new Vue({
  el: '#app',
  data() {
    console.log("App has loaded")
    return {}
  }
})
