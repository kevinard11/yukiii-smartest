#!/home/utils/node-v14.5.0/bin/node
// #!/usr/bin/env node
// Same example for .ts typescript

function foo() {
    const arg1 = 'a'
    // let b = see.bar(arg1)
    // see.bar(globalList)

    return globalRunCount
}
function bar( myList ) {
    globalRunCount = globalRunCount + 1
    if ( globalRunCount < 2 ) {
        bar(myList)
    }
    console.log("hello")
    baz()

    return '8'
}
function baz() {
    console.log("world %s", globalList)
}
// main program
const globalRunCount = require('mongodb').MongoClient
globalList = ['a', 'b']
test = foo()
foo("ada")
baz()

app.get('/health', (req, res) => {
    var stat = {
        app: 'OK',
        mongo: mongoConnected
    };
    res.json(stat);
});
app.use(bodyParser.urlencoded({ extended: true }));
app.use(expLogger);
app.use((req, res, next) => {
    res.set('Timing-Allow-Origin', '*');
    res.set('Access-Control-Allow-Origin', '*');
    next();
});
// all categories
app.get('/categories', (req, res) => {
    if(mongoConnected) {
        collection.distinct('categories').then((categories) => {
            res.json(categories);
        }).catch((e) => {
            req.log.error('ERROR', e);
            res.status(500).send(e);
        });
    } else {
        req.log.error('database not available');
        res.status(500).send('database not available');
    }
});