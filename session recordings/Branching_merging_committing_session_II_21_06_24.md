## BRANCHING
Right, what I'm going to do now is I'm going to the, documents that we've already got.

[Peter Murray-Rust] 10:21:38
So if we go to a list and we say get Status then I'm on PMR one. Origin is,I'm never quite sure what origin is, so I'm not going to say anything here.

[Peter Murray-Rust] 10:22:19
Somewhere, these are all the files that I have. Which. But otherwise. All the PMR one branches files are in the system and have been pushed.

[Peter Murray-Rust] 10:22:39
Right. A number of these I'm just checking to see if any of these are important.

[Peter Murray-Rust] 10:22:48
But I don't think so, right. So this is in the branch. Now I'm going to,Check out Which really means switch branches, but the word is check out. A main it used to be called master that was felt to be rather colonial.

[Peter Murray-Rust] 10:23:11
Yes, has been changed to main, but you will still find, tutorials and so on.
That talk about Awesome. Okay. This is up to date as well. So we have 2 branches.

[Peter Murray-Rust] 10:23:28
And we want to synchronize those and we believe that main has got stuff that that, PMR one has it. Now I went to the web to find out how to do this. Let me check for somewhere on that..

## MERGING

[Peter Murray-Rust] 10:24:05
That we put main in.I want to merge the main into branch. That's always safe because it won't hurt main.

[Peter Murray-Rust] 10:24:17
It, Right, so, so you can see why it says main here. Master, but we'll change it to main.

[Peter Murray-Rust] 10:24:27
So, okay, git merged master into branch.

[Peter Murray-Rust] 10:24:36
I had one which I, we don't want to use rebase at all.

[Peter Murray-Rust] 10:24:44
I think it was this one was very simple. So we check out main. All to make sure that it is an up to date.

[Peter Murray-Rust] 10:24:53
We check out our branch. This branch is called valid data. Here this, ours is called PMR one.

[Peter Murray-Rust] 10:25:00
We merge the main and when we push, okay. So that's what we're going to do.

[Peter Murray-Rust] 10:25:04
So here I am. On main, I will, git pull.

[Peter Murray-Rust] 10:25:18
Just to make sure it's up to date. I will check out PMR one.

[Peter Murray-Rust] 10:25:24
Which means change branches.

[Peter Murray-Rust] 10:25:37
Okay. And then we are going to, get, get, Main. So merging main.

[Peter Murray-Rust] 10:25:46
In PMR one. If we are fortunate and there are I don't many changes any any main differences or if you know the files don't overlap.

[Peter Murray-Rust] 10:26:02
This will be straightforward. If however we've got more than one version of the file, we have to take decisions as to which one to do.

[Peter Murray-Rust] 10:26:12
So let's see how this works out. And there's a visual tool which will help us.

[Peter Murray-Rust] 10:26:20
So git merge main

[Peter Murray-Rust] 10:26:26
It's got quite a lot of thinking to do. It's a very sophisticated system is, git.

[Peter Murray-Rust] 10:26:36
Merge conflict in Read. Okay. So Can I do this in `pycharm`,  let me see if this, works in `pycharm`

[Peter Murray-Rust] 10:27:12
Is it a remote? I'll go in here. I have checked out. Main.

[Peter Murray-Rust] 10:27:18
Yeah.

[Peter Murray-Rust] 10:27:26
I saw that it here would actually bring up a visual editor. I'm disappointed it hasn't. Okay

[Peter Murray-Rust] 10:27:57
At least read me is not very very large

[Peter Murray-Rust] 10:28:16
Why? Let's see.

[Peter Murray-Rust] 10:28:26
She's not particularly helpful.

[Peter Murray-Rust] 10:28:38
We haven't even got to read me. On this one.

[Peter Murray-Rust] 10:29:32
Right, there's a lot of differences here.

[Peter Murray-Rust] 10:29:37
Oh, of course it may be to read me at the top.

[Peter Murray-Rust] 10:29:44
Hey, this is just a subdirectory.

[Peter Murray-Rust] 10:29:59
I hope it's not going to do it on every file.

[Peter Murray-Rust] 10:30:18
Right, so yes, so. It's not been able to merge. This here so.

[Peter Murray-Rust] 10:30:29
That's actually put both of those in and see if it. If it manages this.

[Peter Murray-Rust] 10:31:01
Okay, so we've edited that maybe.

[Peter Murray-Rust] 10:31:17
Okay, I wish it would actually tell us which the, merged files were.

[Peter Murray-Rust] 10:31:34
I can get some idea of this.

[Peter Murray-Rust] 10:31:47
So I'm going to have to.

[Peter Murray-Rust] 10:31:52
Go back to the web and look for this. These have obviously diverged more, than they should do.

[Peter Murray-Rust] 10:32:00
And this is a reason for not keeping your branches widely separated.

[Peter Murray-Rust] 10:32:14
I'm gonna look for how to do this.

[Sravya] 10:33:13
Okay. I think, the, I mean, the both files are not merged .

[Peter Murray-Rust] 10:33:22
No, they, no, it's not merging. We want to, merge them.

[Peter Murray-Rust] 10:33:29
Right.

[Sravya] 10:34:34
In that case, you can merge the, files in GitHub.

[Peter Murray-Rust] 10:34:42
Right, do you know how to do this?

[Sravya] 10:34:45
So I just asked the Google how to do that and

[Sravya] 10:34:54
I think it should be only done in GitHub.

[Peter Murray-Rust] 10:35:08
This is I mean, I've run into these sorts of problems before. I wish it said which the files were.

[Peter Murray-Rust] 10:35:16
I mean. I'm going to go back and see what. Clearly.

[Peter Murray-Rust] 10:35:48
I'll have to think. 

[Peter Murray-Rust] 10:36:10
Maybe it's just to read me, so git add file.

[Peter Murray-Rust] 10:36:33
Let me try again.

[Peter Murray-Rust] 10:37:15
Okay, so.

[Peter Murray-Rust] 10:37:19
Okay, let me try to merge. Which am I on? I'm on Branch PMR one, that's fine.

[Peter Murray-Rust] 10:37:27
So I'm gonna go back to the merge, and see what happens.

[Peter Murray-Rust] 10:37:32
No.

[Peter Murray-Rust] 10:37:39
Okay.

[Peter Murray-Rust] 10:37:50
Right, okay, now if I am lucky, it's push those files to git.

[Peter Murray-Rust] 10:38:19
Recent pushes, okay. Well, on Main, Main contains ALIS, right?

[Peter Murray-Rust] 10:38:29
We go to PMR one.

[Peter Murray-Rust] 10:38:32
Yeah. And it's now got a list, right? Is that right?

[Sravya] 10:38:33
Yeah.

## FRICTIONS IN MERGING

[Peter Murray-Rust] 10:38:59
So 1st of all, Many thanks to both of you for your. It is a It is a patient area this.

[Peter Murray-Rust] 10:39:10
Secondly, It is incredibly complicated. Git. And, You work by having a small number of commands that you know work and when you run into problems you take things very, very slowly.

[Sravya] 10:39:35
Yes.

[Peter Murray-Rust] 10:39:35
We didn't, we didn't go off. And find commands like rebase everything. Minus fix it or something of that sort.

[Peter Murray-Rust] 10:39:45
We came down to the situation where there was one file which was a problem. No, I don't actually care what that file looks like.

[Peter Murray-Rust] 10:40:00
Yes, certainly got stuff at the bottom there. It's actually got both of them in.

[Peter Murray-Rust] 10:40:08
The merge is very powerful. And occasionally, crypts up on very small problems but it's an incredibly powerful system and if it is used , then, you find that there are very few, problems, and that you have to, that what you have to do is just keep it up to date No, I've now got a PMR one which is my own and which is compatible with main. So I can now continue to make changes to PMR one.

[Peter Murray-Rust] 10:40:57
And push to PMR one but from time to time we are going to have to then integrate PMR one and and Sravya and Parijat and Nitika and so on with the main, right?

[Peter Murray-Rust] 10:41:13
So we don't want to We don't want to leave that too long. Right, wow.

[Peter Murray-Rust] 10:41:19
That's so. I really thought we were going to be in trouble then, right? So don't be afraid of, of the get commands but if you don't understand them Look them up, look for the simplest ones ask on the slack. Always ask on the slack. If you're unclear, ask for somebody to share a session with you.

## ADDING MARKEDDOWN FILES TO GITHUB

[Peter Murray-Rust] 10:42:50
What are we going to do now?

[Parijat Bhadra] 10:42:53
How do we add the summaries?

[Peter Murray-Rust] 10:42:57
Right. Okay, that's, that's a very good, thing. So let's go through, let's go through that.

[Peter Murray-Rust] 10:43:38
Right. Okay. What about you, Parijat? Have you anything in, Markdown ?

[Parijat Bhadra] 10:43:41
yeah, I did it on Mark Down and like, saved it as an HTML file. I didn't summarize it. I cleaned it up a bit.

[Peter Murray-Rust] 10:45:42
Right.

[Peter Murray-Rust] 10:46:02
In the summary, What I'm going to suggest is we make one sentence for each of these, right?

[Peter Murray-Rust] 10:46:13
So, If you can open a file. Which, now this is a good question as to where the file is.

[Peter Murray-Rust] 10:49:58
What's the name of the file?

[Parijat Bhadra] 10:50:02
This is open notebook and semantic climate.

[Peter Murray-Rust] 10:50:06
Right, okay.

[Parijat Bhadra] 10:50:25
Then this was a little bit on `pygetpapers`

[Peter Murray-Rust] 10:50:28
Right. `pygetpapers`, so I get papers is all one word.

[Peter Murray-Rust] 10:50:40
Right. And also a software should always be lower case. So that's,

[Peter Murray-Rust] 10:50:49
It should be lower case. So the P should be. Lower case.

[Peter Murray-Rust] 10:50:58
That's right. And also, it should be, in it should be in, code form.

[Peter Murray-Rust] 10:53:38
That's it. Okay, if you save that. And now, view it.

[Peter Murray-Rust] 10:54:16
Yes. I think you will see that that is a different color. Is that right?

[Parijat Bhadra] 10:54:24
Yes, yes.

[Peter Murray-Rust] 10:54:36
Yes, exactly. Okay, so. Everybody should make sure that The software is always bracketed with an opening and the closing back tick.

## GLOBAL EDITING TOOL

[Peter Murray-Rust] 10:54:56
As you know, it's a universal, convention. Right, so if you go through and make sure now you should be able to do that with a global edit right so do you have a tool which allows you to do a global edit what are we looking at this, what tool are we looking at this 

[Parijat Bhadra] 10:55:18
That's something I wanted to ask you that I understood how we are using regular expression, but I don't know how to bring it into this like, picture like, Exactly.

[Peter Murray-Rust] 10:55:23
Yes.

[Peter Murray-Rust] 10:55:40
We're looking at the documents here what tool is being used to display the documents

[Peter Murray-Rust] 10:56:00
I mean, it says, Dillinger at the top 

[Parijat Bhadra] 10:56:04
Yes, this is one of the like tools of markdown itself. It allows us to write it down on the left side and on the right side we already have the HTML part.

[Peter Murray-Rust] 10:56:16
Brilliant, brilliant. Okay. Well, What you have to do, I'll have a look for this at the moment.

[Peter Murray-Rust] 10:56:24
So, if I Look for global editing.

[Peter Murray-Rust] 10:56:41
Right. So.

[Peter Murray-Rust] 10:58:26
I think you need a local text editor, okay?

[Parijat Bhadra] 10:58:35
Okay.

[Peter Murray-Rust] 10:59:34
Let's put your file in a branch, okay?

[Parijat Bhadra] 10:59:39
Okay.

## SAVING A MARKDOWN FILE

[Peter Murray-Rust] 11:00:56
Indeed. Okay. So, Come out of Dillinger.

[Peter Murray-Rust] 11:01:17
Now, so, okay, before you do that, You've got a version here of your of this. That's in a Google Doc at the moment. Is that right?.

[Parijat Bhadra] 11:01:30
Yes

[Peter Murray-Rust] 11:02:01
So, and this is for everybody. Everybody should have their files in their system.

[Peter Murray-Rust] 11:03:09
Export as marked down.

[Peter Murray-Rust] 11:03:45
Excellent. This is exactly the file you want. This is what you should be working with.

[Sravya] 11:06:28
Oh, Peter, just now I also converted my document into Market and saved it.

[Peter Murray-Rust] 11:06:33
Good. Brilliant. Okay. So.

[Peter Murray-Rust] 11:07:08
Okay, fine. Well, Stavia, can you use the command line?

[Sravya] 11:07:13
Yes, Peter, I can.

[Peter Murray-Rust] 11:07:23
So Sravya, if you can take the screen.

[Sravya] 11:07:44
Yes, Peter. And this is my Markdown.

[Peter Murray-Rust] 11:07:47
Okay, good. What we want to do is just make a Git branch. And, and then commit the file.

[Peter Murray-Rust] 11:07:58
That's all we're going to do at the moment. So. Can you open the command line part of this?

[Sravya] 11:08:07
Yes.

[Peter Murray-Rust] 11:08:29
Okay, so. If you can now go to if you can go to the directory, the repository on your system so this is semantic climate and go to the ALIS 2 0 2 4.

[Peter Murray-Rust] 11:09:25
Excellent, okay. So. Can you type git?

[Sravya] 11:09:38
Okay.

[Peter Murray-Rust] 11:09:41
Alright. So that.

[Sravya] 11:09:44
Just a minute bit. I am just navigating.

[Peter Murray-Rust] 11:09:49
It's all right. I, I, you know, I have the same problem.

[Sravya] 11:09:56
Yeah.

[Sravya] 11:10:17
I don't know what's happening, but I'm

[Peter Murray-Rust] 11:10:18
I see. If you go to If you

[Sravya] 11:10:22
But I can, I can open it in.

[Peter Murray-Rust] 11:10:27
All you need is a file name. So it looks to me as if it should be under wind.

[Peter Murray-Rust] 11:10:35
If you click on the users, it may tell you what the path is. 

[Sravya] 11:11:39
Oh, Peter, can I do it in VS code?

[Peter Murray-Rust] 11:11:40
Yes, do it in VS code

[Sravya] 11:11:43
Okay. I have semantic climate here.

[Peter Murray-Rust] 11:11:50
Right. Okay. Right. What we're going to have to do is to find the gIt extension in VS code.

[Peter Murray-Rust] 11:11:58
So this is useful.

[Sravya] 11:12:17
Yes. I got it.

[Peter Murray-Rust] 11:12:18
Right, so type dir there and see what happens.

[Sravya] 11:12:22
Okay.

[Peter Murray-Rust] 11:12:24
Right. Do you recognize? Yes, ALIS 2024. Right.

[Peter Murray-Rust] 11:12:30
Do you see that?

[Sravya] 11:12:32
Yes.

[Peter Murray-Rust] 11:12:33
Okay, that's fine. So for some reason you're called HP, right? That's fine.

[Peter Murray-Rust] 11:12:43
So. If you should have a, so what you can do is use get. So if you go to the left hand side.

[Peter Murray-Rust] 11:12:55
There's a row of icons. And now go right over to your left margin.

[Peter Murray-Rust] 11:13:02
And. Go to the top left of your window. There, yeah, left, left. Yeah.

[Sravya] 11:13:10
Yeah.

[Peter Murray-Rust] 11:13:12
The next one, that's kit. Click on it.

[Peter Murray-Rust] 11:13:22
Right. 

[Peter Murray-Rust] 11:13:29
I'm not sure what it's showing me that this. If you go, okay, try it on the command line, go down to a very bottom and type git.

[Peter Murray-Rust] 11:13:39
Okay.

[Peter Murray-Rust] 11:13:43
Good, you got Git in the system. Okay. Now do git status.

[Peter Murray-Rust] 11:13:53
Yep. You're on branch PMR one great you want to make a new branch right so you say git Branch.

[Peter Murray-Rust] 11:14:10
And now let's. Call it Sravya or whatever, right? I  think no minus.
.
[Peter Murray-Rust] 11:14:28
I think you should put your name in it so that we know so and don't put minus.

[Sravya] 11:14:34
Oh, okay.

[Peter Murray-Rust] 11:14:48
Right, now. You're now on your branch. Just do git status.

[Sravya] 11:14:49
Yes.

[Peter Murray-Rust] 11:15:01
Right, your branch is up to date.

[Peter Murray-Rust] 11:15:05
I know. With that, just try git make, make a file. Just make an edit.

[Peter Murray-Rust] 11:15:20
Edit a read me file or something like that.

[Peter Murray-Rust] 11:15:26
So we're work, wait, We are, which one are we working on?

[Peter Murray-Rust] 11:15:35
We're working on ALIS 2024 yes, and but. Oh.

[Peter Murray-Rust] 11:15:43
This is open notebook, right, okay. So let's. Open a new file in

[Sravya] 11:15:47
Yes, Peter.

[Peter Murray-Rust] 11:15:56
Open a new file in VS code. Just a new file. And we will call it summary.

[Sravya] 11:16:07
Okay.

[Peter Murray-Rust] 11:16:20
No, put some summary, open notebook, right? We may need to make extra branches at the moment, but you're writing a summary about Open Notebook.

[Peter Murray-Rust] 11:16:32
So summary_open notebook.

[Peter Murray-Rust] 11:16:36
That's right.

[Peter Murray-Rust] 11:16:40
oh, let's make it a mark down file.

[Sravya] 11:16:51
Okay.

[Peter Murray-Rust] 11:16:52
Right. Okay. And now let's just put in this, put in hash.

[Peter Murray-Rust] 11:17:01
Yes, space. Summary of. Open notebook, underscore.

[Peter Murray-Rust] 11:17:15
Whatever the file was called open notebook.

[Sravya] 11:17:15
Okay. underscore?

[Peter Murray-Rust] 11:17:22
Yeah. No, just put space.

[Sravya] 11:17:29
Okay.

[Peter Murray-Rust] 11:17:31
Section. It doesn't really matter what we've got in because we're going to edit it right.

[Peter Murray-Rust] 11:17:38
And then type. After this, put us a new line. And put Summary of Topics

[Sravya] 11:17:49
With hash.

[Peter Murray-Rust] 11:17:50
Hey, it's a good no, no hash. Good idea to put a blank line here.

[Sravya] 11:17:52
Okay.
.
[Peter Murray-Rust] 11:17:59
Summary of topics in.

[Peter Murray-Rust] 11:18:04
And what was the file called?

[Peter Murray-Rust] 11:18:11
Let me see if I've got it on mine. So just, I's half a minute.

[Peter Murray-Rust] 11:18:36
It was called Open note_semantic.

[Peter Murray-Rust] 11:18:48
Okay, that's fine. That's all you need to do at the moment. And then, let's save that file.

[Sravya] 11:18:58
Okay. Yes.

## ADDING A FILE TO GIT

[Peter Murray-Rust] 11:19:01
Right and now let's go to git

[Peter Murray-Rust] 11:19:07
And say git status.

[Peter Murray-Rust] 11:19:11
And it should tell us we got a new file. Right, do you see that?

[Sravya] 11:19:15
Yes, Peter.

[Peter Murray-Rust] 11:19:16
Right, on track. So you've got to add that now. You can either add it in VS Code or you can add it directly here. So let's add it directly here. Git_Space , Add. And then this file, summary note. Yeah.

[Sravya] 11:19:46
Is that okay?

[Peter Murray-Rust] 11:19:46
Good. Yeah, that's absolutely fine. Now do git status again.

[Peter Murray-Rust] 11:19:57
And what you'll see now is You've got a change to be committed. Do you see that?

[Sravya] 11:20:04
Yes, Peter.

[Peter Murray-Rust] 11:20:04
So the red one was not in the system. The green one is in the system. So what we now do is, we have to commit it.

[Peter Murray-Rust] 11:20:18
So we say git commit - "am".

[Peter Murray-Rust] 11:20:44
And say, added summary for Open Notebook session.

[Peter Murray-Rust] 11:20:58
Right, okay. Return.

[Peter Murray-Rust] 11:21:05
So. It tells you it's done it. Now do git status again.

[Sravya] 11:21:09
Yes.

[Peter Murray-Rust] 11:21:18
And now it says your branch is ahead of origin PMR one by one commit. So you've got to push it so git push.

[Sravya] 11:21:24
Yes, Peter.

[Peter Murray-Rust] 11:21:32
That's it.

## ADDING SRAVYA AS A CONTRIBUTOR ON GITHUB

[Peter Murray-Rust] 11:21:41
Oh, okay. You don't have Permission here, right? So you have got to leave your screen as it is.

[Peter Murray-Rust] 11:22:08
You won't see this on your screen. Let me just,

[Peter Murray-Rust] 11:22:33
So I'm going to speak what I do. Maybe I will take the screen and show you, how we do this.

[Sravya] 11:22:44
Yes.

[Peter Murray-Rust] 11:23:07
Right, can you see the screen? So this is our repository. Let's just have a look and see what branches we've got on this.

[Sravya] 11:23:18
Yes.

[Peter Murray-Rust] 11:23:18
We got quite a lot of branches but we don't have yet have yours so what we're going to do is add you as a contributor.

[Peter Murray-Rust] 11:23:29
So to do that. I have to remember how to do it.

[Peter Murray-Rust] 11:23:43
Sorry, go to settings. I go to collaborators.

[Peter Murray-Rust] 11:24:01
Right, I now add people. So I have to add you to this report and you have to do this for every repository, right?

[Sravya] 11:24:23
Okay.

[Peter Murray-Rust] 11:25:22
Invite collaborator.You Well now get an email which you have to reply to.

[Sravya] 11:25:32
Yes, Peter, I will check it.

[Sravya] 11:25:46
Yeah, I got the mail

[Peter Murray-Rust] 11:25:48
Right, okay, so now I go back to Semantic climate

[Sravya] 11:26:02
It is saying that I now have the push access.

[Peter Murray-Rust] 11:26:05
Excellent. Okay, so now I go to settings, Collaborators

[Peter Murray-Rust] 11:26:14
Are you seeing my screen still?

[Sravya] 11:26:16
Yes, yes, Peter.

[Peter Murray-Rust] 11:26:46
Okay.

[Peter Murray-Rust] 11:27:24
Right here. Oh, you already have access to this. 

[Sravya] 11:27:28
Yes.

[Peter Murray-Rust] 11:27:35
No, you need to take the screen back, right?

[Sravya] 11:27:39
Yes, we do.

[Peter Murray-Rust] 11:27:45
And already and did you okay you take the screen back so I need to stop sharing the screen.

[Sravya] 11:27:51
Yeah.

[Sravya] 11:28:05
Can you see my screen?

[Peter Murray-Rust] 11:28:06
It's brilliant. Yeah. Okay.

## NEW BRANCH

[Sravya] 11:28:13
I'm doing this.

[Peter Murray-Rust] 11:28:14
Yeah, yeah, it's a game.

[Sravya] 11:28:18
Yeah, that.

[Peter Murray-Rust] 11:28:18
Brilliant. Okay.

[Peter Murray-Rust] 11:28:32
Do git status. I'm not sure you pushed it to the right branch. Just do git status.

[Sravya] 11:28:39
Oh.

[Peter Murray-Rust] 11:28:44
Right, okay. Do git checkout. Sravya or whatever you called it.

[Peter Murray-Rust] 11:28:56
No, let's make a change to that. And what was the file called?

[Peter Murray-Rust] 11:29:16
It's called summary_open notebook, isn't it? So.

[Sravya] 11:29:21
Yes.

[Peter Murray-Rust] 11:29:25
You've now got to Cd ALIS 2 0 2 4. So.

[Peter Murray-Rust] 11:29:30
At the bottom, CD ALIS 2024. Now.

[Peter Murray-Rust] 11:29:43
Now do you have a text editor? Just Right, okay. This is going to be a bit messy.

[Peter Murray-Rust] 11:29:58
Let's make a new file here. So I'm going to have a new file. Say and simply

[Sravya] 11:30:02
Okay.

[Peter Murray-Rust] 11:30:10
Yeah, make a new file. Oh, wait a minute. Can, you can edit it here.

[Sravya] 11:30:13
Yes.

[Peter Murray-Rust] 11:30:16
Can you edit this file? Yes, I did edit that file.

[Sravya] 11:30:18
This file. I mean.

[Sravya] 11:30:24
I mean you want to, rename it? 

[Peter Murray-Rust] 11:30:27
No, just do any. Yes, okay. And now put in.

[Peter Murray-Rust] 11:30:35
Put in a new line. and put in let's put in a let's use alis so put in * opennotebook philosophy

[Peter Murray-Rust] 11:31:15
That's all right Okay. Now save that file.

[Sravya] 11:31:21
Yeah, saved.

[Peter Murray-Rust] 11:31:22
Right, go back to your. Command line.

[Peter Murray-Rust] 11:31:28
And do git status.

[Peter Murray-Rust] 11:31:33
Right. So you've got a new file there, right? So you can now, do

[Peter Murray-Rust] 11:31:51
Git add..summary. Just copy the red thing.

[Sravya] 11:32:00
Okay. This thing.

[Peter Murray-Rust] 11:32:02
Yeah, you should be able to cut and paste it. 

[Peter Murray-Rust] 11:32:22
Now do git Commit-am "summary_opennotebook"

[Sravya] 11:32:47
Okay.

[Peter Murray-Rust] 11:32:52
Yep. And now, do, Git push.

[Sravya] 11:32:54
Yeah.

[Peter Murray-Rust] 11:33:04
Right. This is the 1st time you've done it, so you have to copy that thing in the middle.

[Peter Murray-Rust] 11:33:11
Between the blank lines git push Copy the whole of that into your paste buffer.

[Sravya] 11:33:18
Okay.

[Peter Murray-Rust] 11:33:19
And then. That's it.

[Peter Murray-Rust] 11:33:27
Right, and you have now pushed this to the repository. And. What we're now going to do, is have a look at the, so you pushed it right.

[Parijat Bhadra] 11:33:39
Okay.

[Peter Murray-Rust] 11:33:43
Now we are going to show how I pull it into my into my session. Right. So you stop stop sharing.

[Sravya] 11:33:52
Yes.

[Peter Murray-Rust] 11:34:18
Okay. So I'm now in semantic climate.

[Peter Murray-Rust] 11:34:37
And now we should have Branch Sravya, okay?

[Peter Murray-Rust] 11:34:43
So let's have a look at that. You've got all sorts of things here, but in alis 2 0 2 4.

[Sravya] 11:34:44
Yeah.

[Peter Murray-Rust] 11:34:54
You should have.

[Peter Murray-Rust] 11:34:57
What was the file called?

[Sravya] 11:35:00
Summary opennotebook.

[Peter Murray-Rust] 11:35:09
Yes, we've got that. Right, okay. And we got that there. Now.

[Peter Murray-Rust] 11:35:15
Let's have a look and see what I've got. So I, so. Mentally remember that.

[Peter Murray-Rust] 11:35:25
Actually what we can do is we can Open another window.

[Peter Murray-Rust] 11:35:54
And now I'm going to select my branch PMR One And. I'm going to, at your branch, put it up there.

[Peter Murray-Rust] 11:36:24
And I'm going to look at my branch here.

[Peter Murray-Rust] 11:36:36
Right, so you can see that my version is different from yours.

## MERGING TWO VERSIONS 

[Peter Murray-Rust] 11:36:48
Right, and that's perfectly okay. So you've got that in there. So. What I'm going to do now is I'm going to merge.

[Sravya] 11:36:51
Yes.

[Peter Murray-Rust] 11:36:58
Your version into mine. At least I hope I am. And then I'm probably going to crash.

[Peter Murray-Rust] 11:37:09
So I'll do this on the command line, I hope.

[Peter Murray-Rust] 11:37:20
cd alis2024

[Peter Murray-Rust] 11:37:24
I'm going to get pull. You should always do that. And that actually pulls the whole repository.

[Peter Murray-Rust] 11:37:32
So you can see here that it tells me there's a new branch.

[Sravya] 11:37:36
Yeah.

[Peter Murray-Rust] 11:37:37
Right, so what I'm going to do now is I'm going to Merge that branch in so This is on my machine. So this is on PMR one and this is on Sravya, so if I go to my thing here. I'm on PMR 

[Peter Murray-Rust] 11:38:06
So I'm not a going to say more.

[Peter Murray-Rust] 11:38:15
What's the file called?

[Peter Murray-Rust] 11:38:19
Summary.

[Peter Murray-Rust] 11:38:41
Okay, I'm going to Git merge and I'm going to go back and look up. How we doing?

[Peter Murray-Rust] 11:38:57
I'm going to check out yours and I'm going to merge it into PMR one. 

[Peter Murray-Rust] 11:39:30
That's git merged.

[Peter Murray-Rust] 11:40:04
Merge conflict so it didn't, it wasn't able to do it, right?

[Peter Murray-Rust] 11:40:11
So we will open the open notebook.

[Peter Murray-Rust] 11:40:38
Not quite sure. Why can't do that?

[Peter Murray-Rust] 11:41:05
And ought to do.

[Peter Murray-Rust] 11:41:10
I'll create my own one here.

[Peter Murray-Rust] 11:41:43
Let's see if it allows me to merge now.

[Peter Murray-Rust] 11:42:27
You can, you know, I don't want to frighten you about git, but, merging is at the limit as to what we can do.

[Peter Murray-Rust] 11:42:47
Right, you have an unfinished merge. These context must be resolved. This is the file.

[Peter Murray-Rust] 11:42:55
You and if I say merge. It now gives me a 3 way Version. So this is what we're going to end up with.

[Peter Murray-Rust] 11:43:05
This is what you've got and this is what I've got. So. Right, so I want to include yours.

[Sravya] 11:43:11
Yes.

[Peter Murray-Rust] 11:43:16
So what I do is, there are 2 things you can either omit yours or you can omit this one.

[Peter Murray-Rust] 11:43:29
Or you can, sorry, you can either. Take your one or you can omit it.

[Peter Murray-Rust] 11:43:35
So we're going to take yours. And this is what we've got here.

[Peter Murray-Rust] 11:43:43
So we're going to say we're going to apply at the bottom. And now I hope that that is now going to allow me to git merge that

[Peter Murray-Rust] 11:44:02
Right, it's merged it. Okay, I'm now going to say git commit. I'm now going to git push.

[Peter Murray-Rust] 11:44:36
Right, so now let us go to git.

[Peter Murray-Rust] 11:44:45
Here is your file. On Sravya branch. If we go to PMR branch,

[Peter Murray-Rust] 11:44:56
And look at this. It's the same. So do you see that we have in incorporated your version into my question..

[Sravya] 11:45:10
Yes, . Yeah.

[Peter Murray-Rust] 11:45:11
Right. Now. If I were giving a formal lecture I would have prepared that better. Do you see what I mean?

[Peter Murray-Rust] 11:45:23
But it's worked. So I don't want you to feel merging is a major problem. The main thing to do is to make sure that you frequently commit things because that will save things and you can always backtrack on them.


[Peter Murray-Rust] 11:45:49
And what we need to do now, and decide between the 2 of you is, that this is a really useful session on how to, use git to, maintain parallel branches and merge things.

[Peter Murray-Rust] 11:46:06
Okay.