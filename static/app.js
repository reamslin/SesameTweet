$('#feed').on("click", ".load", async function (evt) {
    const resp = await axios.get($('#feed').attr('data-api') + $('#feed').attr('data-page'));
    evt.target.remove()
    console.log(resp)
    for (let tweetData of resp.data.tweets) {
        let $newTweet = $(generateTweetHTML(tweetData));
        $('#feed').append($newTweet)
    }
    if (!resp.data.end) {
        $newButton = $(`<button class='btn-home center load'>View More</button>`)
        $('#feed').append($newButton)
    }
    $('#feed').attr('data-page', resp.data.page)
})


function generateTweetHTML(tweet) {
    return `
    <div class='container p-2 mx-4 mb-4 feed_box'>
        <img style='margin-bottom: 10px; margin-right: 10px' src=${tweet.character.image}>
        <b><a class='text-my-own-color' href=' /authors/${tweet.character.id}'>${tweet.character.name}</a></b>
        <div class='float-right'>
        <a class='float-right' href='https://www.twitter.com/${tweet.character.screen_name}/status/${tweet.twitter_id}'>
                <i class='fa fa-twitter-square fa-2x'></i></a>
            <div class='mr-2 tweet-text float-right'>${tweet.month} - ${tweet.day} - ${tweet.year}
            </div>

        </div>
        <div class='tweet-text'>${tweet.text}
        </div>`
        +
        generateMediaHTML(tweet.media)
        +
        `</div>`

}

function generateMediaHTML(media) {
    var html = '';
    for (m of media) {
        html += `<div class='bg-dark'>`
        if (m.media_type === 'video') {
            html += `
                <video controls class='media img-fluid' poster=${m.media_url}>`
                +
                generateSourcesHTML(m.sources)
                +
                `</video>`
        } else if (m.media_type === 'photo') {
            html += `<img class='media img-fluid' src=${m.media_url}>`
        }
        html += `</div>`
    }
    return html
}

function generateSourcesHTML(sources) {
    var html = ''
    for (source of sources) {
        html += `<source src=${source.url} type="${source.content_type}"></source>`
    }
    return html
}