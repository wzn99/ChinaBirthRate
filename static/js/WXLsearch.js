$(document).ready(function(){
    // 点击检索按钮，发请求
    $("#chatbotsendbtn").on("click", function () {
        var searchtext = $.trim($('#chattextarea').val());
        if (searchtext == "") {
           alert("请输入您的问题");
           return;
        }

        // 将问题添加到聊天窗口的末尾
        var question_html = '<div class="item item-right">'
                        + '<div class="bubble bubble-right">' + searchtext + '</div>' 
                        + '<div class="avatar avatar-user"></div>'
                        + '</div>';
        $('.content').append(question_html);
        // 清空问题文本框
        $('#chattextarea').val('');
        $('#chattextarea').focus();
        // 滚动条置底
        var height = $('.content').scrollTop();
        $(".content").scrollTop(height);

        $.ajax({
            type: "get",
            url: "/searchanswer",
            data: {
                "id": $("#chatbotsendbtn").attr("id"), 
                "text": searchtext
            },
            dataType: "json",
            beforeSend: function() {
                // 设置disabled阻止用户继续点击
                $("#chatbotsendbtn").attr("disabled", "disabled");
            }, 
            complete: function () {
                // 请求完成移除 disabled 属性
                $("#chatbotsendbtn").removeAttr("disabled");
            },  
            success: function(result){
                if(result.status == 200){
                    // 将答案添加到聊天窗口的末尾
                    var answer_html = '<div class="item item-left">'
                        + '<div class="avatar avatar-bot"></div>'
                        + '<div class="bubble bubble-left">' + result.answer + '</div>' 
                        + '</div>';
                    $('.content').append(answer_html);
                    // 滚动条置底
                    var height = $('.content').scrollTop();
                    $(".content").scrollTop(height);
                    console.log("检索答案成功");
                }
                else{
                    // 将答案添加到聊天窗口的末尾
                    var answer_html = '<div class="item item-left">'
                        + '<div class="avatar avatar-bot"></div>'
                        + '<div class="bubble bubble-left">对不起！我不明白您的问题，可以换种问法吗？</div>' 
                        + '</div>';
                    $('.content').append(answer_html);
                    // 滚动条置底
                    var height = $('.content').scrollTop();
                    $(".content").scrollTop(height);
                    console.log("检索不到答案");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常："+e);
            }
        });
    })

    // 点击索引按钮，发请求
    $("#submit2index").on("click", function () {
        $.ajax({
            type: "post",
            url: "/buildindex",
            data: {"id": $("#submit2index").attr("id")},
            dataType: "json",
            beforeSend: function() {
                // 设置disabled阻止用户继续点击
                $("#submit2index").attr("disabled", "disabled");
            }, 
            complete: function () {
                // 请求完成移除 disabled 属性
                $("#submit2index").removeAttr("disabled");
            },  
            success: function(result){
                if(result.status == 200){
                    console.log(result.text);
                }else{
                    alert("索引失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常："+e);
            }
        });
    })
    // 点击检索按钮，发请求
    $("#btn-submit2search").on("click", function () {
        var keyword = $.trim($('input[name="submit2search"]').val());
        if (keyword == "")
            return;
        $.ajax({
            type: "get",
            url: "/searchindex",
            data: {
                "id": $("#submit2search").attr("id"), 
                "keyword": keyword
            },
            dataType: "json",
            beforeSend: function() {
                // 设置disabled阻止用户继续点击
                $("#btn-submit2search").attr("disabled", "disabled");
            }, 
            complete: function () {
                // 请求完成移除 disabled 属性
                $("#btn-submit2search").removeAttr("disabled");
            },  
            success: function(result){
                if(result.status == 200){
                    var weibo_list = result.text;
                    var weibo_oldlist = $("tr.movie-entry");
                    if (weibo_oldlist && weibo_oldlist.length>0) {
                        // 清空原有表格
                        $("tr.movie-entry").remove();
                        $("ul.pagination").remove();
                    }
                    // 创建搜索结果的表格并插入到前端页面
                    for (var i = 0; i < weibo_list.length; i++) {
                        var search_html = '<tr class="movie-entry">' 
                        + '<td>' + weibo_list[i].id + '</td>' 
                        + '<td>' + weibo_list[i].blogger_name + '</td>'
                        + '<td>' + weibo_list[i].blogger_home + '</td>'
                        + '<td>' + weibo_list[i].weibo_content + '</td>'
                        + '<td><input id="{{ data.id }}" type="button" class="btn btn-success btn-pos" value="词性标注"><input id="{{ data.id }}" type="button" class="btn btn-success btn-ner" value="实体识别"></td>'
                        + '</tr>';
                        $("table#moview-result-list-table").append($(search_html))
                    }
                    console.log("检索成功");
                }else if(result.status == 201){
                    alert("检索不到任何结果!");
                }
                else{
                    alert("检索失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常："+e);
            }
        });
    })
    // 点击词性标注按钮，发请求
    $("input.btn-pos").on("click", function () {
        $.ajax({
            type: "get",
            url: "/posannotation",
            data: {
                "id": $(this).attr("id")
            },
            dataType: "json",
            beforeSend: function() {
                // 设置disabled阻止用户继续点击
                $(this).attr("disabled", "disabled");
            }, 
            complete: function () {
                // 请求完成移除 disabled 属性
                $(this).removeAttr("disabled");
            },  
            success: function(result){
                if(result.status == 200){
                    var movie_data = result.data;
                    var replace_html = '<tr class="movie-entry" id=' + movie_data.id + '>' 
                        + '<td>' + movie_data.id + '</td>' 
                        + '<td>' + movie_data.blogger_name + '</td>'
                        + '<td>' + movie_data.blogger_home + '</td>'
                        + '<td>' + movie_data.weibo_content + '</td>'
                        + '<td><input id="{{ data.id }}" type="button" class="btn btn-success btn-pos" value="词性标注"><input id="{{ data.id }}" type="button" class="btn btn-success btn-ner" value="实体识别"></td>'
                        + '</tr>';
                    $("tr.movie-entry#"+movie_data.id).replaceWith(replace_html);
                }else{
                    alert("失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常："+e);
            }
        });
    })
    // 点击实体识别按钮，发请求
    $("input.btn-ner").on("click", function () {
        $.ajax({
            type: "get",
            url: "/nerannotation",
            data: {
                "id": $(this).attr("id")
            },
            dataType: "json",
            beforeSend: function() {
                // 设置disabled阻止用户继续点击
                $(this).attr("disabled", "disabled");
            }, 
            complete: function () {
                // 请求完成移除 disabled 属性
                $(this).removeAttr("disabled");
            },  
            success: function(result){
                if(result.status == 200){
                    var movie_data = result.data;
                    // 清空字体颜色
                    $("tr.movie-entry#"+movie_data.id).css("color", "");
                    var replace_html = '<tr class="movie-entry" id=' + movie_data.id + '>' 
                        + '<td>' + movie_data.id + '</td>' 
                        + '<td>' + movie_data.blogger_name + '</td>'
                        + '<td>' + movie_data.blogger_home + '</td>'
                        + '<td>' + movie_data.weibo_content + '</td>'
                        + '<td><input id="{{ data.id }}" type="button" class="btn btn-success btn-pos" value="词性标注"><input id="{{ data.id }}" type="button" class="btn btn-success btn-ner" value="实体识别"></td>'
                        + '</tr>';
                    $("tr.movie-entry#"+movie_data.id).replaceWith(replace_html);
                }else{
                    alert("失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常："+e);
            }
        });
    })

    // 点击问题索引按钮，发请求
    $("#submit3index").on("click", function () {
        $.ajax({
            type: "post",
            url: "/buildquestionindex",
            data: {"id": $("#submit3index").attr("id")},
            dataType: "json",
            beforeSend: function() {
                // 设置disabled阻止用户继续点击
                $("#submit3index").attr("disabled", "disabled");
            },
            complete: function () {
                // 请求完成移除 disabled 属性
                $("#submit3index").removeAttr("disabled");
            },
            success: function(result){
                if(result.status == 200){
                    console.log(result.text);
                }else{
                    alert("索引失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常："+e);
            }
        });
    })
})
