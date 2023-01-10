sentimentData = []

// parsing the tweets and getting only the use information 
let tweetParser = async function (tweetDom) {
    let tweetContent = tweetDom.innerText;
    let tweet = {
      name: "",
      username: "",
      time: "",
      content: "",
      interaction: {
        reply: "",
        retweets: "",
        like: "",
      },
    };
 
    let timeElm = tweetDom.getElementsByTagName("time")[0];
    let timeDis = ""
    if (timeElm && timeElm.innerText){
        timeDis = timeElm.innerText
    } 
    let dateTimeAtri = ""
    if (timeElm && timeElm.getAttribute("datetime")){
        dateTimeAtri = timeElm.getAttribute("datetime")
    } 
    let splitTweet = tweetContent.split(/\n/);
    let splitLength = splitTweet.length;
    let breakpoint = 4;
    let endContent = splitLength - 4;
    for (let i = 0; i < splitLength; i++) {
      if (splitTweet[i] === timeDis) {
        breakpoint = i;
      }
    }

    tweet.name = splitTweet[0];
    tweet.username = splitTweet[1];
    tweet.time = dateTimeAtri;
    tweet.content = splitTweet.slice(breakpoint + 1, endContent + 1);
    tweet.content = tweet.content.join("\n");
    tweet.interaction.reply = splitTweet[endContent + 1];
    tweet.interaction.retweets = splitTweet[endContent + 2];
    tweet.interaction.like = splitTweet[endContent + 3];

    return tweet;
  };

 // getting tweets using the DOM scraping
async function getTweets() {
    
    let divs = document.querySelectorAll("article");
    tweets = [];
    tweetIds = [];
    for (let div of divs) {
        let dataTestId = div.getAttribute("data-testid");
        if (dataTestId == "tweet") {  
            tweets.push(div);
        }
    } 
  
    tweetContent = {};
    let parsedTweets = {};
  
    for (let tweet of tweets) {

        let aTags = tweet.getElementsByTagName("a");
        for (let aTag of aTags) {
            let href = aTag.getAttribute("href");
            if (href.includes("/status/")) {
                let start = href.indexOf("/status/");
                let tweetId = href.split("/status/");
                tweetId = tweetId[1];
                
                if (!(tweetId in parsedTweets)) {
                    tweetIds.push(tweetId);
                    parsedTweets[tweetId] = await tweetParser(tweet);
                }
            }
        } // Finding Tweet Id for every tweet by processing all <a> tags within the tweet
    } // Iterating through tweets
    return parsedTweets;
}

async function domUpdate() {
    let divagain = document.querySelectorAll("article");
    for (let div of divagain) {
        let dataTestId = div.getAttribute("data-testid");
        sentimentData.filter(e =>{
            if(div.innerText.includes(e.tweet_text)){
                if (dataTestId == "tweet") {
                    val = div.getElementsByTagName('time')
                    check = val[0]?.innerHTML?.includes("Detected Mood:")
                    if (!check && val[0]){
                         if (e.detected_mood == "POSITIVE"){
                            val[0].innerHTML += " Detected Mood: "+`&#128522;`
                        }else if(e.detected_mood == "NEGATIVE"){
                            val[0].innerHTML += " Detected Mood: "+`&#128533;`
                        }else{
                            val[0].innerHTML += " Detected Mood: "+`&#128528;`
                        }
                    }
                }
            }
        })
    }
}

let prepLangobj = async function (newDistinctTweets){
    requestobj= []
    for (let i in newDistinctTweets){
        if(newDistinctTweets[i].content!= "" && !requestobj.filter(e => e.tweet_text === newDistinctTweets[i].content).length > 0){
            requestobj.push({"tweet_text":newDistinctTweets[i].content})
        }
    }
    res = await langdetect(requestobj)

}

let langdetect = async function (requestobj){ 
    const url = "https://twit-sentiment.xe.tansanrao.net/api/language-detection";
    requestobj2 = []
    const options = {
    method: "POST",
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestobj),
    };
    fetch(url, options)
    .then((response) => response.json())
    .then((data) => {
        console.log("datatatatatatat1",data);
        for(let i in data){ 
           if(data[i].is_english)
           requestobj2.push({"tweet_text":data[i].tweet_text})
        }
        if (requestobj2.length > 0 ) {
            res2 = sentimentAnalysis(res)
        }
    });
    return requestobj2
}

let sentimentAnalysis = function (requestobj){
    const url = "https://twit-sentiment.xe.tansanrao.net/api/sentiment-score";
    const options = {
    method: "POST",
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestobj),
    };
    fetch(url, options)
    .then((response) => response.json())
    .then((data) => {
        for(let i in data){ 
            if(sentimentData.length == 0 || sentimentData.filter(e => e.tweet_text != data[i].tweet_text)){
            sentimentData.push(data[i])
            }
        }
    });    
}
// end of all the functions

  
// main function 
let parsedTweetsGlobal = {};
let main = async function () {
let parsedTweetsGlobal = {};
parsedTweetsGlobal = await getTweets();
  
window.addEventListener("scroll", async function () {
    let newParsedTweets = await getTweets();
    let newDistinctTweets = new Object();
    for (let newTweetID in newParsedTweets) {
        if (!(newTweetID in parsedTweetsGlobal)) {
            newDistinctTweets[newTweetID] = newParsedTweets[newTweetID];
        }
    }
    await prepLangobj(newDistinctTweets)
    await domUpdate()
    parsedTweetsGlobal = { ...parsedTweetsGlobal, ...newParsedTweets };
});
};
main();

  