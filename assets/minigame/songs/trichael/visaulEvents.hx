var whiteTint:FlxSprite;
var blackTint:FlxSprite;

function onCreatePost(){
    whiteTint = new FlxSprite();
    whiteTint.makeGraphic(4000, 4000, 0xFFFFFFFF);
    whiteTint.scale.set(1.5, 1.5);
    whiteTint.scrollFactor.set();
    
    blackTint = new FlxSprite();
    blackTint.makeGraphic(4000, 4000, 0xFF000000);
    blackTint.scale.set(1.5, 1.5);
    blackTint.scrollFactor.set();

    add(whiteTint);
    add(blackTint);

    camHUD.alpha = 0;
    skipCountdown = true;
}

function onStepHit() {
    if (curStep == 99){
        FlxTween.tween(blackTint, {alpha: 0});
        FlxTween.tween(camHUD, {alpha: 1});
    }
    if (curStep == 114)
        FlxTween.tween(whiteTint, {alpha: 0});        
    if (curStep == 1012){
        FlxTween.tween(blackTint, {alpha: 1});
        FlxTween.tween(camHUD, {alpha: 0});
    }
    if (curStep == 1028){
        FlxTween.tween(blackTint, {alpha: 0}, 0.5);
        FlxTween.tween(camHUD, {alpha: 1}, 0.5);
    }
    if (curStep == 1680)
        FlxTween.tween(whiteTint, {alpha: 1}, 2);
    if (curStep == 1808){
        FlxTween.tween(blackTint, {alpha: 1});
        FlxTween.tween(camHUD, {alpha: 0});
    }
}